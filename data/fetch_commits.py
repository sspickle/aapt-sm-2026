#!/usr/bin/env python3
"""Fetch index.qmd commit timestamps for every repo that had a feedback request.

Why
---
repos.tsv carries only repo createdAt and a commit COUNT, and the graded-PDF
filenames carry a date with no time. Date-only comparison silently drops the
most interesting case: a student who requests feedback at 14:00 and commits at
18:00 the same day did act on it, but `request.date() < commit.date()` is False.

Exact commit times make "did they do more work after asking?" answerable.

Only repos appearing in issues.tsv are fetched (~113, not all 453).

Output: commits.tsv  ->  org, repo, committed_at   (gitignored)
Resumable: existing rows are kept and only missing repos are fetched.
"""

import collections
import csv
import json
import pathlib
import subprocess
import sys

D = pathlib.Path(__file__).parent
OUT = D / "commits.tsv"


def repos_with_requests():
    seen = []
    with open(D / "issues.tsv") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) >= 2 and (row[0], row[1]) not in seen:
                seen.append((row[0], row[1]))
    return seen


def already_fetched():
    done = collections.defaultdict(int)
    if OUT.exists():
        with open(OUT) as f:
            for row in csv.reader(f, delimiter="\t"):
                if len(row) >= 3:
                    done[(row[0], row[1])] += 1
    return done


def fetch(org, repo):
    """-> [committed_at, ...] for index.qmd, newest first. [] if none/inaccessible."""
    cmd = ["gh", "api", "-X", "GET", f"repos/{org}/{repo}/commits",
           "-f", "path=index.qmd", "-f", "per_page=100"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return None
    try:
        return [c["commit"]["committer"]["date"] for c in json.loads(p.stdout)]
    except Exception:
        return None


def main():
    targets = repos_with_requests()
    done = already_fetched()
    todo = [t for t in targets if t not in done]
    print(f"repos with feedback requests: {len(targets)}")
    print(f"  already fetched: {len(done)}   to fetch: {len(todo)}")
    if not todo:
        print("nothing to do")
        return

    mode = "a" if OUT.exists() else "w"
    ok = empty = fail = 0
    with open(OUT, mode, newline="") as f:
        w = csv.writer(f, delimiter="\t")
        for i, (org, repo) in enumerate(todo, 1):
            dates = fetch(org, repo)
            if dates is None:
                fail += 1
                print(f"  [{i}/{len(todo)}] FAIL {org}/{repo}", file=sys.stderr)
                continue
            if not dates:
                empty += 1
            for d in dates:
                w.writerow([org, repo, d])
            ok += 1
            if i % 20 == 0:
                f.flush()
                print(f"  [{i}/{len(todo)}] ...")
    print(f"done: {ok} repos fetched ({empty} had no index.qmd history), {fail} failed")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
