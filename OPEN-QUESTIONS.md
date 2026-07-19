# Open questions — pre-grade feedback analysis

Started 2026-07-19, the morning of the SM26 talk. **Deliberately not in the
talk**: the numbers below rest on too many unexamined exclusions to say out
loud. Written down so the thread can be picked up cold.

## The question

Of the feedback requests students made, how many happened **before the
instructor saw the report**? If most feedback arrives before the instructor
ever looks, the tool is doing formative work rather than functioning as a
post-grade appeal channel.

## Method

`data/pre_grade_feedback.py` joins three sources:

| source | role |
|---|---|
| `issues.tsv` | every AI-feedback request, exact UTC timestamp |
| `usage_clean.csv` | authoritative `repo → student` map |
| graded PDFs in Drive | one file per grading pass |

**Do not re-parse repo names.** `extract_components()` from
`build_quarto_reports` is written for build-script *directory* names and
mangles these slugs (`p1-time-constant-jsmith42` → username `constant-jsmith42`;
`lab-4-feedback-<user>` → empty). `usage_clean.csv` already has the mapping.

### Two possible cutoffs, and why it matters

PDF filenames come from `copy_and_rename_pdfs.py` as
`{username}-[{number}-]{project}-{date}.pdf`, where `date` is
`git log -1 --date=short -- index.qmd` — **the student's last commit, not a
grading date.**

`copy_and_rename_pdfs.py` uses `shutil.copy2`, which preserves mtime, so the
PDF's mtime is when `index.pdf` was *rendered* — when the instructor collected
and read it.

- **render time (mtime)** → "before I saw it" ← the question asked
- **last commit (filename)** → "before they stopped editing"

A PDF with no grade recorded still counts as "I saw it" — that case means
feedback was given and a resubmit requested.

## Current numbers (treat as provisional)

```
MATCHED requests: 119
  before I rendered/read it : 112 (94%)
  after                     :   7  (6%)
  pairs with >=1 pre-read request: 73 / 77

  [alt cutoff] before student's last commit: 31 (26%)
```

## The finding that actually deserves attention

The 94% is close to structural — students work during the assignment window,
the instructor collects at the end, so of course most requests precede the
render. It confirms the tool isn't a post-grade appeal channel, which is worth
knowing but not surprising.

**The 26% is the interesting one.** Only about a quarter of requests came
before the student's final commit. Roughly three-quarters of the time a student
requested feedback and then *did not touch the report again* before collection.
Feedback was frequently the last action rather than the start of a revision
loop.

That sits in tension with the revision-window finding (backup slide 2: heavy
feedback users needed a second revision pass 0 / 56 times). Both can be true —
front-loaded fixes could mean less revision was *needed* — but the tension
should be resolved before either is presented as a story about behaviour.

## Why these numbers are not talk-ready

**135 of 254 requests are excluded.** Specifically:

- **72 from unmapped repos** — includes `*-template` repos and the instructor's
  own test repos. Legitimate to drop, but never audited one by one.
- **63 unmatched to a grading record** — 44 where the student was graded on
  *other* assignments but not this one, 19 from students with no graded PDF at
  all. The 44 is the suspicious group: is that a naming gap, or assignments
  genuinely never collected?
- **30 PDFs still unparsed** — naming variants the regex misses
  (`...-p-update5-...`, `...-labp1-...`).

**Unverified assumption:** mtime survives `shutil.copy2`, but Google Drive sync
can rewrite mtimes. Spot-check a few files against when you actually rendered
them. If a whole course collapses onto one date, the cutoff is contaminated.

## UPDATE (same day): exact commit times are now available

`data/fetch_commits.py` pulls `index.qmd` commit timestamps from the GitHub API
for every repo that had a feedback request (143 repos, 0 failures) into
`commits.tsv`. This changes two things.

**It fixes a precision bug in the 26%.** The filename date *is* the last commit
to `index.qmd`, so "before last commit" was already the right metric — but
compared date-only. A student who requested feedback at 14:00 and committed at
18:00 the same day was counted as NOT having acted on it. That is the most
common iterative pattern, so the 26% is a floor, not an estimate. Recompute
`pre_grade_feedback.py` against `commits.tsv` before believing any version of
that number.

**It made the cold open verifiable.** `data/find_cold_open.py` reconstructs
push -> feedback -> fix per request and found 62 requests acted on within 6
hours (22 evening/overnight, 35 with <=5 min turnaround, median 3.9 min),
including one that matches the cold-open story almost exactly. Those aggregates
ARE safe to state: they need only commit and issue timestamps, both exact, with
no join to grading records — which is precisely what makes the numbers further
up this page fragile.

**Note:** the template repo (`...-p1-time-constant-template`) and the
instructor's own test repos score highly in the candidate search. Filter them
before drawing any conclusion; they are not students.

## Next steps, in order

1. **Recompute against `commits.tsv`** with exact timestamps instead of
   date-only comparison — this alone may move the 26% substantially.
2. Audit the 44 "graded on other assignments" pairs — naming gap or real gap?
3. Handle the 30 unparsed PDF names.
4. Confirm the mtime assumption against a few known render sessions.
5. Recompute. If the ratio survives at ~90% of requests included, it is sayable.
6. Resolve the 26% against the revision finding before telling either as a story.
7. The obvious missing instrument is still a three-question exit survey. None of
   this log archaeology answers *why*.

## Reproducing

```bash
uv run data/pre_grade_feedback.py     # writes data/pre_grade_feedback.csv
```

Output is gitignored — it contains student usernames.
