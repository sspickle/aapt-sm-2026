#!/usr/bin/env python3
"""Find real instances of the cold-open story, so it can be told without inventing it.

The story:
    "A student pushed a lab report at 11 PM, got feedback in about a minute,
     fixed two things, and pushed again before midnight. I hadn't looked at it yet."

Reconstructed per feedback request:
    T0  last index.qmd commit BEFORE the request  -> the push
    T1  the AI Feedback issue's created_at        -> feedback arrived
    T2  index.qmd commits AFTER T1                -> the fixes
    turnaround = T1 - T0

All GitHub timestamps are UTC; reported in America/Indiana/Indianapolis, since
the claim is about what the clock on the wall said.

Ranks candidates by how closely they match: late evening, fast turnaround, and
at least one follow-up commit the same night.

Prints to stdout only — output contains usernames, so nothing is written to disk.
"""

import collections
import csv
import datetime as dt
import pathlib
import sys
from zoneinfo import ZoneInfo

D = pathlib.Path(__file__).parent
TZ = ZoneInfo("America/Indiana/Indianapolis")
UTC = dt.timezone.utc


def load_commits():
    by_repo = collections.defaultdict(list)
    with open(D / "commits.tsv") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) < 3:
                continue
            t = dt.datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
            by_repo[(row[0], row[1])].append(t)
    for k in by_repo:
        by_repo[k].sort()
    return by_repo


def load_requests():
    by_repo = collections.defaultdict(list)
    with open(D / "issues.tsv") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) < 3:
                continue
            t = dt.datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
            by_repo[(row[0], row[1])].append(t)
    for k in by_repo:
        by_repo[k].sort()
    return by_repo


def main():
    commits = load_commits()
    requests = load_requests()
    cands = []

    for key, reqs in requests.items():
        hist = commits.get(key, [])
        if not hist:
            continue
        for t1 in reqs:
            before = [c for c in hist if c <= t1]
            if not before:
                continue
            t0 = before[-1]
            turnaround = (t1 - t0).total_seconds() / 60.0
            # follow-up commits within 6h of feedback (same working session)
            after = [c for c in hist if t1 < c <= t1 + dt.timedelta(hours=6)]
            if not after:
                continue
            gap = (after[-1] - t1).total_seconds() / 60.0
            l0, l1, l2 = (t.astimezone(TZ) for t in (t0, t1, after[-1]))
            evening = l0.hour >= 19 or l0.hour < 5
            same_night = l2.date() == l0.date() or l2.hour < 5
            score = (
                (3 if evening else 0)
                + (3 if turnaround <= 5 else 2 if turnaround <= 15 else 0)
                + (2 if same_night else 0)
                + (2 if len(after) >= 2 else 1)
            )
            cands.append({
                "score": score, "org": key[0], "repo": key[1],
                "push": l0, "feedback": l1, "last_fix": l2,
                "turnaround_min": turnaround, "fixes": len(after),
                "fix_gap_min": gap, "evening": evening, "same_night": same_night,
            })

    cands.sort(key=lambda c: (-c["score"], c["turnaround_min"]))
    print(f"{len(cands)} request(s) followed by a commit within 6h\n")
    print("TOP CANDIDATES (local time, America/Indianapolis)")
    print("=" * 78)
    for c in cands[:12]:
        tag = []
        if c["evening"]:
            tag.append("EVENING")
        if c["same_night"]:
            tag.append("SAME NIGHT")
        print(f"[score {c['score']}] {c['org']}  {c['repo']}   {' '.join(tag)}")
        print(f"    pushed    {c['push']:%a %b %d  %-I:%M %p}")
        print(f"    feedback  {c['feedback']:%-I:%M %p}   "
              f"(+{c['turnaround_min']:.1f} min)")
        print(f"    {c['fixes']} follow-up commit(s), last at "
              f"{c['last_fix']:%-I:%M %p} (+{c['fix_gap_min']:.0f} min)")
        print()

    ev = [c for c in cands if c["evening"]]
    fast = [c for c in cands if c["turnaround_min"] <= 5]
    print("=" * 78)
    print(f"summary: {len(cands)} acted-on requests | {len(ev)} in the evening "
          f"| {len(fast)} with <=5 min turnaround")
    if cands:
        med = sorted(c["turnaround_min"] for c in cands)[len(cands) // 2]
        print(f"         median turnaround: {med:.1f} min")


if __name__ == "__main__":
    main()
