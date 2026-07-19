#!/usr/bin/env python3
"""Propose GitHub-username -> Brightspace-student matches, then report usage vs grades.

Pass 1 (this run): print a proposed mapping for human verification.
Any line marked ??? needs a human decision.
"""
import csv, os, re, collections, statistics, pathlib, difflib

D = pathlib.Path(__file__).parent
GRADES = pathlib.Path(os.path.expanduser("~/Downloads/grades"))
OVERRIDE = D / "gh_to_student.csv"   # optional human-supplied mapping

ORG_FOR = {
    "Scientific Computing":      "202520-PHYS-280",
    "Laboratory Instrumentation":"202520-PHYS-230",
    "Interfacing Laboratory":    "202520-EENG-340",
}

def isnum(x):
    try:
        float(x); return True
    except Exception:
        return False

def pct(n, d):
    return 100.0*float(n)/float(d) if isnum(n) and isnum(d) and float(d) else None

# ---------- usage ----------
usage = collections.defaultdict(int)      # (org, gh) -> total rounds
repos_n = collections.defaultdict(int)
for r in csv.DictReader(open(D / "usage_clean.csv")):
    usage[(r["org"], r["student"])] += int(r["rounds"])
    repos_n[(r["org"], r["student"])] += 1
gh_by_org = collections.defaultdict(list)
for (org, s) in sorted(usage):
    gh_by_org[org].append(s)

# ---------- grades ----------
students = collections.defaultdict(list)
for f in sorted(GRADES.glob("*.csv")):
    org = next((o for k, o in ORG_FOR.items() if k in f.name), None)
    if not org:
        continue
    with open(f, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        continue
    cols = list(rows[0].keys())
    sub_n = next((c for c in cols if re.search(r"(Projects|Labs) Subtotal Numerator", c)), None)
    sub_d = next((c for c in cols if re.search(r"(Projects|Labs) Subtotal Denominator", c)), None)
    fin_n = next((c for c in cols if c.startswith("Calculated Final Grade Numerator")), None)
    fin_d = next((c for c in cols if c.startswith("Calculated Final Grade Denominator")), None)
    for row in rows:
        last  = (row.get("Last Name") or "").strip()
        first = (row.get("First Name") or "").strip()
        if not (last or first):
            continue
        students[org].append(dict(
            last=last, first=first,
            email=(row.get("Email") or "").strip(),
            d2l=(row.get("Username") or "").strip().lstrip("#"),
            report=pct(row.get(sub_n), row.get(sub_d)),
            final=pct(row.get(fin_n), row.get(fin_d)),
        ))

# ---------- matching ----------
def keys_for(s):
    """candidate strings a github username might resemble"""
    l, f = s["last"].lower(), s["first"].lower()
    em = s["email"].split("@")[0].lower() if s["email"] else ""
    d2 = s["d2l"].lower()
    out = {l, f+l, l+f, (f[:1]+l if f else ""), (l+f[:1] if f else ""),
           (f+l[:1] if l else ""), em, d2}
    return {k for k in out if k}

def score(gh, s):
    g = re.sub(r"[^a-z0-9]", "", gh.lower())
    g = re.sub(r"\d+$", "", g)
    g = re.sub(r"uindy$", "", g)
    best = 0.0
    for k in keys_for(s):
        kk = re.sub(r"[^a-z0-9]", "", k)
        if not kk:
            continue
        r = difflib.SequenceMatcher(None, g, kk).ratio()
        if kk and (g.startswith(kk) or kk.startswith(g)):
            r = max(r, 0.90)
        best = max(best, r)
    return best

override = {}
if OVERRIDE.exists():
    for row in csv.DictReader(open(OVERRIDE)):
        override[(row["org"], row["github"])] = row["email"] or row["d2l"]

print("=" * 78)
print("PROPOSED MAPPING  (verify the ??? lines)")
print("=" * 78)
resolved = {}
for org in sorted(gh_by_org):
    pool = students.get(org, [])
    print(f"\n--- {org}  ({len(gh_by_org[org])} github users, {len(pool)} enrolled) ---")
    taken = set()
    for gh in gh_by_org[org]:
        key = (org, gh)
        if key in override:
            tgt = override[key]
            m = next((s for s in pool if tgt in (s["email"], s["d2l"])), None)
            if m:
                resolved[key] = m; taken.add(id(m))
                print(f"  [set] {gh:<22} -> {m['first']} {m['last']}")
                continue
        cands = sorted(((score(gh, s), s) for s in pool if id(s) not in taken),
                       key=lambda t: -t[0])
        if not cands:
            print(f"  ???  {gh:<22} -> (no candidates left)")
            continue
        top, s = cands[0]
        runner = cands[1][0] if len(cands) > 1 else 0
        if top >= 0.80 and top - runner >= 0.08:
            resolved[key] = s; taken.add(id(s))
            print(f"  ok   {gh:<22} -> {s['first']} {s['last']}   ({top:.2f})")
        else:
            alts = ", ".join(f"{c[1]['first']} {c[1]['last']}({c[0]:.2f})" for c in cands[:3])
            print(f"  ???  {gh:<22} -> {alts}")
    unmatched = [s for s in pool if id(s) not in taken]
    if unmatched:
        print(f"       unmatched students: "
              + ", ".join(f"{s['first']} {s['last']}" for s in unmatched))

print("\n" + "=" * 78)
print(f"auto-resolved {len(resolved)} of {sum(len(v) for v in gh_by_org.values())} github users")
print("=" * 78)

# ---------- if enough resolved, report usage vs grade ----------
pairs = []
for (org, gh), s in resolved.items():
    if s["report"] is None:
        continue
    pairs.append((org, usage[(org, gh)], repos_n[(org, gh)], s["report"], s["final"]))

if len(pairs) >= 10:
    print("\nUSAGE vs REPORT SCORE (aggregate only)")
    used   = [p[3] for p in pairs if p[1] > 0]
    unused = [p[3] for p in pairs if p[1] == 0]
    if used:
        print(f"  ever used feedback : n={len(used):>3}  mean report {statistics.mean(used):.1f}%"
              f"  median {statistics.median(used):.1f}%")
    if unused:
        print(f"  never used         : n={len(unused):>3}  mean report {statistics.mean(unused):.1f}%"
              f"  median {statistics.median(unused):.1f}%")
    bands = collections.defaultdict(list)
    for org, rounds, nrep, rep, fin in pairs:
        b = "0" if rounds == 0 else ("1-2" if rounds <= 2 else ("3-5" if rounds <= 5 else "6+"))
        bands[b].append(rep)
    print("\n  by total feedback requests:")
    for b in ["0", "1-2", "3-5", "6+"]:
        if bands[b]:
            print(f"    {b:<5} n={len(bands[b]):>3}  mean report {statistics.mean(bands[b]):.1f}%")
    xs = [p[1] for p in pairs]; ys = [p[3] for p in pairs]
    if len(xs) > 2 and statistics.pstdev(xs) and statistics.pstdev(ys):
        mx, my = statistics.mean(xs), statistics.mean(ys)
        cov = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / len(xs)
        r = cov / (statistics.pstdev(xs)*statistics.pstdev(ys))
        print(f"\n  Pearson r (requests vs report score) = {r:+.2f}  (n={len(xs)})")
else:
    print("\nNot enough resolved matches to report grades. Fill in gh_to_student.csv:")
    print("  org,github,email,d2l")
