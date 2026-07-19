# AI Feedback on Student Lab Reports — AAPT Summer Meeting 2026

Slides and analysis code for a 10-minute talk given at the AAPT Summer Meeting,
Pasadena, July 2026.

**Steve Spicklemire**, University of Indianapolis · `spicklemire@uindy.edu`

## What the talk is about

Students write lab reports as Quarto documents in a GitHub repo, work in
Codespaces (no local install), and can request AI feedback on a draft while
there is still time to act on it. Feedback is generated criterion-by-criterion
against an instructor-written rubric and posted back as a GitHub Issue.

It is an **experience report, not a controlled study** — the system was built
while teaching with it. One term, three courses: 43 students, 440 repos,
191 feedback requests.

## Contents

```
presentation.qmd    the deck (Quarto → reveal.js)
timing.md           speaker notes: per-slide budget, prepped Q&A, caveats
images/             screenshots used in the deck
data/               analysis scripts (see note below)
```

Render with:

```bash
quarto render presentation.qmd
```

The rendered HTML is not committed — build it yourself.

## A note on the data

**No student data is in this repository, and none will be added.**

The numbers in the talk come from the GitHub API joined to Brightspace
gradebook exports. Those intermediate files carry GitHub usernames, student
emails, and D2L IDs joined to grades — FERPA-protected education records — so
`.gitignore` excludes `data/*.csv` and `data/*.tsv` categorically.

What *is* here is the analysis code (`mine_usage.sh`, `analyze.py`,
`join_grades.py`, `rebuild.py`, `regrades.py`). It is published so the method
is inspectable, not so the results are reproducible — you would need your own
course data to run it.

Everything reported in the deck is aggregate, with a smallest cell size of 12.

## Tools referenced

- [`UINDY-INSTRUCTORS/gh-rba`](https://github.com/UINDY-INSTRUCTORS/gh-rba) —
  `gh` CLI extension for distributing assignment repos (replaces GitHub
  Classroom, which is being retired)
- `UINDY-INSTRUCTORS/ai-feedback-system` — the feedback Action
- `UINDY-INSTRUCTORS/batch_quarto_reports` — batch rendering for grading

## License

Slides and notes: CC BY 4.0. Code: MIT.
