#!/usr/bin/env python3
"""Mine Notability grading files for regrade behaviour, cross with feedback usage."""
import os, re, csv, glob, collections, statistics, pathlib

# Local path to the graded-PDF archive. Override with NOTABILITY_DIR.
B = pathlib.Path(os.environ.get("NOTABILITY_DIR", "~/Notability")).expanduser()
D = pathlib.Path(__file__).parent
ORG = {"ph280": "202520-PHYS-280", "ph230": "202520-PHYS-230", "eeng-340": "202520-EENG-340"}

# Non-student accounts to drop from the analysis: an instructor account and a
# student-assistant account, neither enrolled. Real usernames are deliberately
# not in this repo — supply them via EXCLUDE_ACCOUNTS as "org:username,org:username".
EXCLUDE = {
    tuple(pair.split(":", 1))
    for pair in os.environ.get("EXCLUDE_ACCOUNTS", "").split(",")
    if ":" in pair
}

recs = []
for course, org in ORG.items():
    root = B / f"{course}-252"
    if not root.exists():
        continue
    for f in root.rglob("*.note"):
        n = f.name[:-5]
        # student = leading token before the first course/proj marker
        m = re.match(r"^(.+?)-(?:ph\d+|proj|p\d|eeng|fp|final)", n, re.I)
        stu = m.group(1) if m else n.split("-")[0]
        stu = re.sub(r"-\d{1,2}$", "", stu)            # AlejandroMR-24 -> AlejandroMR
        stu = re.sub(r"\s*\(\d+\)$", "", stu).strip()
        regrade = bool(re.search(r"regrade", n, re.I))
        dm = re.search(r"(20\d{6})", n)
        recs.append(dict(org=org, student=stu, file=n, regrade=regrade,
                         date=dm.group(1) if dm else None,
                         assignment=f.parent.name))

# fold to (org, student, assignment): did an original and/or regrade exist
key = collections.defaultdict(lambda: dict(orig=0, regrade=0))
for r in recs:
    k = (r["org"], r["student"], r["assignment"])
    key[k]["regrade" if r["regrade"] else "orig"] += 1

# usage
usage = collections.defaultdict(int)
for r in csv.DictReader(open(D / "usage_clean.csv")):
    usage[(r["org"], r["student"])] += int(r["rounds"])

# normalise notability student names against the usage roster (case-insensitive)
roster = {}
for (org, s) in usage:
    roster[(org, s.lower())] = s
def canon(org, s):
    return roster.get((org, s.lower()))

per_stu = collections.defaultdict(lambda: dict(items=0, regrades=0))
unmatched = collections.Counter()
for (org, stu, asg), v in key.items():
    c = canon(org, stu)
    if not c:
        unmatched[(org, stu)] += 1
        continue
    if (org, c) in EXCLUDE:
        continue
    per_stu[(org, c)]["items"] += 1
    if v["regrade"]:
        per_stu[(org, c)]["regrades"] += 1

print("=" * 68)
print("REGRADE BEHAVIOUR vs FEEDBACK USE")
print("=" * 68)
print(f"note files scanned: {len(recs)}")
if unmatched:
    print(f"unmatched name tokens (ignored): {len(unmatched)} -> "
          f"{', '.join(f'{s}' for (_, s), _ in unmatched.most_common(8))}")
print()

band = collections.defaultdict(list)
for k, v in per_stu.items():
    u = usage.get(k, 0)
    b = "0" if u == 0 else ("1-2" if u <= 2 else "3+")
    rate = 100 * v["regrades"] / v["items"] if v["items"] else 0
    band[b].append((rate, v["regrades"], v["items"]))

print(f"{'requests':<10}{'n':>4}{'mean regrade rate':>20}{'total regrades':>16}")
for b in ["0", "1-2", "3+"]:
    g = band[b]
    if not g:
        continue
    print(f"{b:<10}{len(g):>4}{statistics.mean(r for r, _, _ in g):>19.1f}%"
          f"{sum(x for _, x, _ in g):>16}")

allv = [v for v in per_stu.values()]
tot_r = sum(v["regrades"] for v in allv)
tot_i = sum(v["items"] for v in allv)
print(f"\noverall: {tot_r} regraded of {tot_i} graded items ({100*tot_r/tot_i:.0f}%)")

# did regraders also use feedback?
usedset = {k for k in per_stu if usage.get(k, 0) > 0}
regset = {k for k, v in per_stu.items() if v["regrades"] > 0}
both = usedset & regset
print(f"\nstudents who used feedback: {len(usedset)}")
print(f"students who regraded:      {len(regset)}")
print(f"both:                       {len(both)}")
print(f"regraded but never used feedback: {len(regset - usedset)}")
print(f"used feedback but never regraded: {len(usedset - regset)}")
