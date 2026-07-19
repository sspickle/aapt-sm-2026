#!/usr/bin/env python3
"""Rebuild usage stats with a correct student roster, and join to Brightspace grades.

Fixes vs the first pass:
  - drops template repos (name contains 'template')
  - drops instructor repos (sspickle / stevespicklemire)
  - merges GitHub's '-1' duplicate-repo suffix into the base student
  - identifies students as repo-suffixes appearing >= MIN_REPOS times,
    discarding parse fragments ('data', 'integration', ...)
"""
import csv, glob, os, re, collections, statistics, pathlib

D = pathlib.Path(__file__).parent
GRADES = pathlib.Path(os.path.expanduser("~/Downloads/grades"))
MIN_REPOS = 4
INSTRUCTOR = re.compile(r"^(sspickle|stevespicklemire)(-\d+)?$", re.I)
DROP_ORGS = {"202520-EENG-405"}

# ---------- load repos ----------
repos = []
for line in open(D / "repos.tsv"):
    p = line.rstrip("\n").split("\t")
    if len(p) < 5:
        continue
    org, name, iss, commits, created = p[0], p[1], int(p[2]), int(p[3]), p[4]
    if org in DROP_ORGS or "template" in name.lower():
        continue
    repos.append(dict(org=org, repo=name, commits=commits, created=created))

by_org = collections.defaultdict(list)
for r in repos:
    by_org[r["org"]].append(r["repo"])

def build_slugs(names):
    c = collections.Counter()
    for n in names:
        parts = n.split("-")
        for i in range(1, len(parts)):
            c["-".join(parts[:i])] += 1
    return {s for s, k in c.items() if k >= 3}

slugs = {o: build_slugs(n) for o, n in by_org.items()}

def split_repo(org, name):
    cands = [s for s in slugs[org] if name.startswith(s + "-")]
    if not cands:
        return None, None
    a = max(cands, key=len)
    return a, name[len(a) + 1:]

for r in repos:
    a, s = split_repo(r["org"], r["repo"])
    r["assignment"] = a
    r["student"] = re.sub(r"-\d+$", "", s) if s else None   # merge -1 duplicates

# ---------- real rosters ----------
counts = collections.defaultdict(collections.Counter)
for r in repos:
    if r["student"] and not INSTRUCTOR.match(r["student"]):
        counts[r["org"]][r["student"]] += 1

roster = {o: {s for s, n in c.items() if n >= MIN_REPOS} for o, c in counts.items()}

print("=" * 66)
print("CORRECTED ROSTERS (GitHub usernames with >= %d repos)" % MIN_REPOS)
print("=" * 66)
for o in sorted(roster):
    print(f"  {o:<20} {len(roster[o]):>3} students")
print()

student_repos = [r for r in repos
                 if r["student"] in roster.get(r["org"], set())]

# ---------- deployed filter ----------
dep = {}
for line in open(D / "deployed.tsv"):
    p = line.rstrip("\n").split("\t")
    if len(p) == 3:
        dep[(p[0], p[1])] = (p[2] == "YES")
elig = [r for r in student_repos if dep.get((r["org"], r["assignment"]), False)]

# ---------- issues ----------
issues = []
for line in open(D / "issues.tsv"):
    p = line.rstrip("\n").split("\t")
    if len(p) < 4 or p[0] in DROP_ORGS:
        continue
    issues.append(dict(org=p[0], repo=p[1], created=p[2], title=p[3]))
rounds = collections.Counter((i["org"], i["repo"]) for i in issues)
for r in elig:
    r["rounds"] = rounds.get((r["org"], r["repo"]), 0)

print("=" * 66)
print("CORRECTED USAGE")
print("=" * 66)
allstu = {(r["org"], r["student"]) for r in elig}
used_repos = [r for r in elig if r["rounds"] > 0]
per_stu = collections.Counter()
for r in elig:
    per_stu[(r["org"], r["student"])] += r["rounds"]
everused = {k for k, v in per_stu.items() if v > 0}

print(f"student repos (deployed):  {len(elig)}")
print(f"distinct students:         {len(allstu)}")
print(f"feedback requests:         {sum(r['rounds'] for r in elig)}")
print(f"repos that used it:        {len(used_repos)} ({100*len(used_repos)/len(elig):.0f}%)")
print(f"students who ever used it: {len(everused)} ({100*len(everused)/len(allstu):.0f}%)")
never = sum(1 for v in per_stu.values() if v == 0)
tried = sum(1 for v in per_stu.values() if v in (1, 2))
hab   = sum(1 for v in per_stu.values() if v >= 3)
print(f"never / tried / habitual:  {never} / {tried} / {hab}")
print()
for o in sorted({r['org'] for r in elig}):
    e = [r for r in elig if r["org"] == o]
    u = [r for r in e if r["rounds"] > 0]
    print(f"  {o:<20} repos={len(e):>4} used={len(u):>3} ({100*len(u)/len(e):>3.0f}%) "
          f"reqs={sum(r['rounds'] for r in e):>4}")

# ---------- decay, recomputed on clean repos ----------
rm = collections.Counter(r["created"][:7] for r in student_repos)
im = collections.Counter(i["created"][:7] for i in issues)
print("\ndecay (clean denominators):")
print(f"  {'month':<9}{'repos':>7}{'reqs':>7}{'per repo':>10}")
for m in sorted(set(rm) | set(im)):
    if not ("2026-01" <= m <= "2026-05"):
        continue
    print(f"  {m:<9}{rm[m]:>7}{im[m]:>7}{(im[m]/rm[m] if rm[m] else 0):>10.2f}")

with open(D / "usage_clean.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["org", "assignment", "student", "repo", "commits", "rounds"])
    for r in sorted(elig, key=lambda x: (x["org"], x["assignment"] or "", x["student"])):
        w.writerow([r["org"], r["assignment"], r["student"], r["repo"],
                    r["commits"], r["rounds"]])
print(f"\nwrote {D/'usage_clean.csv'}")
