#!/usr/bin/env python3
"""Analyze AI-feedback usage mined from GitHub Classroom orgs."""
import csv, re, collections, statistics, pathlib

D = pathlib.Path(__file__).parent
INSTRUCTOR = {"sspickle", "spicklemire"}  # exclude instructor test repos

repos = []
with open(D / "repos.tsv") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 5:
            continue
        repos.append(dict(org=p[0], repo=p[1], issues=int(p[2]),
                          commits=int(p[3]), created=p[4]))

issues = []
with open(D / "issues.tsv") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        issues.append(dict(org=p[0], repo=p[1], created=p[2], title=p[3]))

# --- derive assignment slug: longest hyphen-prefix shared by >=3 repos in org ---
by_org = collections.defaultdict(list)
for r in repos:
    by_org[r["org"]].append(r["repo"])

def build_slugs(names):
    counts = collections.Counter()
    for n in names:
        parts = n.split("-")
        for i in range(1, len(parts)):
            counts["-".join(parts[:i])] += 1
    return {s for s, c in counts.items() if c >= 3}

slugs = {org: build_slugs(names) for org, names in by_org.items()}

def split_repo(org, name):
    cands = [s for s in slugs[org] if name.startswith(s + "-")]
    if not cands:
        return None, None
    a = max(cands, key=len)
    return a, name[len(a) + 1:]

for r in repos:
    r["assignment"], r["student"] = split_repo(r["org"], r["repo"])

repo_index = {(r["org"], r["repo"]): r for r in repos}
for i in issues:
    r = repo_index.get((i["org"], i["repo"]))
    i["assignment"] = r["assignment"] if r else None
    i["student"] = r["student"] if r else None

# --- filter to real student repos ---
student_repos = [r for r in repos
                 if r["student"] and r["student"] not in INSTRUCTOR
                 and r["commits"] > 0]
student_issues = [i for i in issues
                  if i["student"] and i["student"] not in INSTRUCTOR]

print("=" * 62)
print("SCOPE")
print("=" * 62)
print(f"Orgs (courses/terms):     {len(by_org)}")
print(f"Student repos:            {len(student_repos)}")
print(f"Distinct students:        {len({r['student'] for r in student_repos})}")
print(f"Distinct assignments:     {len({(r['org'],r['assignment']) for r in student_repos})}")
print(f"AI feedback issues:       {len(student_issues)}")
print()

print("=" * 62)
print("BY COURSE")
print("=" * 62)
print(f"{'org':<22}{'repos':>7}{'students':>10}{'fb reqs':>9}{'repos w/ fb':>13}")
for org in sorted(by_org):
    rs = [r for r in student_repos if r["org"] == org]
    iss = [i for i in student_issues if i["org"] == org]
    used = {(i["org"], i["repo"]) for i in iss}
    print(f"{org:<22}{len(rs):>7}{len({r['student'] for r in rs}):>10}"
          f"{len(iss):>9}{len(used):>13}")
print()

# --- adoption: which repos ever requested feedback ---
used_repos = {(i["org"], i["repo"]) for i in student_issues}
n_used = sum(1 for r in student_repos if (r["org"], r["repo"]) in used_repos)
print("=" * 62)
print("ADOPTION")
print("=" * 62)
print(f"Repos that requested feedback at least once: "
      f"{n_used}/{len(student_repos)} ({100*n_used/len(student_repos):.1f}%)")

by_student = collections.defaultdict(lambda: [0, 0])  # [repos, fb reqs]
for r in student_repos:
    by_student[r["student"]][0] += 1
for i in student_issues:
    by_student[i["student"]][1] += 1
ever = sum(1 for s, (nr, nf) in by_student.items() if nf > 0)
print(f"Students who ever used it: {ever}/{len(by_student)} "
      f"({100*ever/len(by_student):.1f}%)")
print()
print("Feedback requests per student (top 12):")
for s, (nr, nf) in sorted(by_student.items(), key=lambda kv: -kv[1][1])[:12]:
    if nf:
        print(f"   {nf:>3} reqs across {nr:>2} repos")
print()

# --- iteration depth on repos where it was used ---
per_repo = collections.Counter((i["org"], i["repo"]) for i in student_issues)
dist = collections.Counter(per_repo.values())
print("=" * 62)
print("ITERATION DEPTH (repos that used it)")
print("=" * 62)
for n in sorted(dist):
    bar = "#" * dist[n]
    print(f"  {n} round(s): {dist[n]:>3}  {bar}")
vals = list(per_repo.values())
if vals:
    print(f"\n  mean {statistics.mean(vals):.2f}   median {statistics.median(vals)}   max {max(vals)}")
    multi = sum(1 for v in vals if v > 1)
    print(f"  iterated more than once: {multi}/{len(vals)} ({100*multi/len(vals):.1f}%)")
print()

# --- time of day / day-of-week signal ---
from datetime import datetime
hours = collections.Counter()
for i in student_issues:
    dt = datetime.fromisoformat(i["created"].replace("Z", "+00:00"))
    hours[(dt.hour - 4) % 24] += 1  # crude UTC->Eastern
print("=" * 62)
print("WHEN FEEDBACK IS REQUESTED (approx US Eastern)")
print("=" * 62)
for h in range(24):
    if hours[h]:
        print(f"  {h:02d}:00  {'#' * hours[h]} {hours[h]}")
late = sum(c for h, c in hours.items() if h >= 20 or h < 4)
print(f"\n  between 8pm and 4am: {late}/{sum(hours.values())} "
      f"({100*late/sum(hours.values()):.1f}%)")

# --- write tidy CSV for further work ---
with open(D / "usage_by_repo.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["org", "assignment", "student", "repo", "commits", "feedback_rounds"])
    for r in sorted(student_repos, key=lambda r: (r["org"], r["assignment"] or "", r["student"])):
        w.writerow([r["org"], r["assignment"], r["student"], r["repo"],
                    r["commits"], per_repo.get((r["org"], r["repo"]), 0)])
print(f"\nWrote {D/'usage_by_repo.csv'}")
