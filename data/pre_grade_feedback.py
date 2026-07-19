#!/usr/bin/env python3
"""How many feedback requests did students make BEFORE the instructor saw the report?

Joins:
  1. issues.tsv        — every AI-feedback request, exact UTC timestamp
  2. usage_clean.csv   — authoritative repo -> student mapping (do NOT re-parse
                         repo names; extract_components() is for build-script
                         directory names and mangles these slugs, e.g.
                         p1-time-constant-jsmith42 -> "constant-jsmith42")
  3. graded PDF exports in Google Drive — one file per grading pass

WHICH DATE MEANS "I SAW IT"
---------------------------
PDF names come from build_quarto_reports/copy_and_rename_pdfs.py as
    {username}-[{number}-]{project}-{date}.pdf
where `date` is `git log -1 --date=short -- index.qmd`: the student's LAST
COMMIT, not a grading date. A student can request feedback after their final
commit and before the instructor renders, so that date is the wrong cutoff.

copy_and_rename_pdfs uses shutil.copy2, which preserves mtime, so the PDF's
mtime is when index.pdf was RENDERED — when the instructor collected and read
it. That is the primary cutoff here. Both are reported:

    render time (mtime) -> "before I saw it"            <- the question
    last commit (name)  -> "before they stopped editing"

CAVEAT: mtime survives shutil.copy2, but Google Drive sync can rewrite it.
Batch renders share a timestamp, which is expected (one render per assignment),
but if a whole course collapses onto one date, treat it as suspect.

Only the FIRST grading pass counts as "I saw it"; regrade/chk/check files are
later passes, counted separately.

Output: pre_grade_feedback.csv (gitignored — contains usernames).
"""

import collections
import csv
import datetime as dt
import os
import pathlib
import re
import sys

# Root holding the per-course graded-PDF exports. Override with GRADES_ROOT,
# e.g. ".../GoogleDrive-<account>/My Drive/ Courses".
DRIVE = pathlib.Path(os.environ.get("GRADES_ROOT", "~/grades-root")).expanduser()
COURSE_DIRS = {
    "230/202520/grades": "202520-PHYS-230",
    "280/202520/grades": "202520-PHYS-280",
    "EENG-340 (interfacing lab)/202520/grades": "202520-EENG-340",
}
# <username>-[<course>]-<assignment><rest>. All three of these occur:
#   jsmith42-ph230-p4-20260212      (course marker, hyphenated)
#   mjones99-ph230p3-20260225    (course marker, not hyphenated)
#   alee2026-lab2-20260205     (no course marker at all)
# The username is non-greedy, so hyphenated handles (jsmith42-24,
# mjones99-code, alee2026-uindy) backtrack correctly.
PDF_RE = re.compile(
    r"^(?P<user>.+?)-(?:ph230|ph280|ee340)?-?(?P<rest>(?:p|proj|lab)0*\d+\b.*)$", re.I)
ASSIGN_NUM = re.compile(r"(?:^|[^a-z0-9])(?:p|proj|lab)0*(\d+)", re.I)
DATE8 = re.compile(r"(20\d{6})")
LATER_PASS = re.compile(r"regrade|chk|check", re.I)
D = pathlib.Path(__file__).parent


def assign_no(text):
    m = ASSIGN_NUM.search(text)
    return int(m.group(1)) if m else None


def load_repo_map():
    """repo.lower() -> (org, student.lower()); from the validated usage table."""
    out = {}
    with open(D / "usage_clean.csv") as f:
        for r in csv.DictReader(f):
            out[r["repo"].lower()] = (r["org"], r["student"].lower())
    return out


def load_gradings():
    out, unparsed = {}, []
    for rel, org in COURSE_DIRS.items():
        root = DRIVE / rel
        if not root.exists():
            print(f"  WARNING: missing {root}", file=sys.stderr)
            continue
        for p in root.rglob("*.pdf"):
            m = PDF_RE.match(p.stem)
            if not m:
                unparsed.append(p.name)
                continue
            rest = m.group("rest")
            no = assign_no(rest)
            if no is None:
                unparsed.append(p.name)
                continue
            user = m.group("user").lower()
            later = bool(LATER_PASS.search(rest))
            d = DATE8.search(rest)
            commit = dt.datetime.strptime(d.group(1), "%Y%m%d").date() if d else None
            render = dt.date.fromtimestamp(p.stat().st_mtime)
            rec = out.setdefault((org, user, no),
                                 {"render": None, "commit": None, "passes": 0})
            rec["passes"] += 1
            if not later:
                if rec["render"] is None or render < rec["render"]:
                    rec["render"] = render
                if commit and (rec["commit"] is None or commit < rec["commit"]):
                    rec["commit"] = commit
    return out, unparsed


def load_requests(repo_map):
    out, unknown = collections.defaultdict(list), collections.Counter()
    with open(D / "issues.tsv") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) < 3:
                continue
            org, repo, ts = row[0], row[1], row[2]
            hit = repo_map.get(repo.lower())
            no = assign_no(repo)
            if hit is None or no is None:
                unknown[repo] += 1
                continue
            out[(hit[0], hit[1], no)].append(
                dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
    return out, unknown


def main():
    repo_map = load_repo_map()
    gradings, unparsed = load_gradings()
    requests, unknown = load_requests(repo_map)

    print(f"repo->student map : {len(repo_map)} repos, "
          f"{len({s for _, s in repo_map.values()})} students")
    print(f"graded PDFs       : {len(gradings)} (student, assignment) pairs "
          f"[{len(unparsed)} unparsed]")
    print(f"feedback requests : {sum(len(v) for v in requests.values())} across "
          f"{len(requests)} pairs [{sum(unknown.values())} from unmapped repos]")

    rows, tot = [], collections.Counter()
    no_record = collections.Counter()
    graded_users = {u for (_, u, _) in gradings}

    for (org, user, no), times in sorted(requests.items()):
        g = gradings.get((org, user, no))
        if not g or g["render"] is None:
            tot["unmatched"] += len(times)
            no_record["never graded" if user not in graded_users
                      else "graded, other assignments"] += len(times)
            continue
        cutoff = g["render"]
        before = sum(1 for t in times if t.date() < cutoff)
        tot["before"] += before
        tot["after"] += len(times) - before
        tot["pairs"] += 1
        tot["pairs_with_pre"] += 1 if before else 0
        if g["commit"]:
            tot["before_commit"] += sum(1 for t in times if t.date() < g["commit"])
        rows.append({"org": org, "student": user, "assignment": no,
                     "requests": len(times), "before_render": before,
                     "after_render": len(times) - before,
                     "render_date": cutoff.isoformat(),
                     "last_commit": g["commit"].isoformat() if g["commit"] else "",
                     "grading_passes": g["passes"]})

    if rows:
        with open(D / "pre_grade_feedback.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    matched = tot["before"] + tot["after"]
    print("\n" + "=" * 66)
    print(f"MATCHED requests: {matched}")
    if matched:
        print(f"  BEFORE I rendered/read it : {tot['before']:4d} "
              f"({100*tot['before']/matched:.0f}%)")
        print(f"  after  I rendered/read it : {tot['after']:4d} "
              f"({100*tot['after']/matched:.0f}%)")
        print(f"  student-assignment pairs with >=1 pre-read request: "
              f"{tot['pairs_with_pre']} / {tot['pairs']}")
        print(f"  [alt cutoff] before student's last commit: {tot['before_commit']} "
              f"({100*tot['before_commit']/matched:.0f}%)")
    print(f"\nUNMATCHED requests: {tot['unmatched']}")
    for k, v in no_record.most_common():
        print(f"  {k}: {v}")
    if unknown:
        print(f"  unmapped repos ({len(unknown)}): {list(unknown)[:3]}")
    if unparsed:
        print(f"  unparsed PDFs ({len(unparsed)}): {unparsed[:3]}")
    print("=" * 66)


if __name__ == "__main__":
    main()
