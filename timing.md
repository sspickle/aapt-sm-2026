# Timing Script — AAPT 2026, 10-minute slot

**Budget: 8:00 speaking + 2:00 Q&A.** Nine slides + 2 backup. If you hit slide 6 at 5:00 you're on pace.

| # | Slide | Target | Cumulative |
|---|-------|--------|------------|
| 1 | Title | 0:15 | 0:15 |
| 2 | The Problem | 0:45 | 1:00 |
| 3 | The Stack | 0:45 | 1:45 |
| 4 | Codespaces | 1:05 | 2:40 |
| 5 | Collaboration | 0:55 | 3:35 |
| 6 | AI Feedback — How | 1:05 | **4:40** |
| 7 | AI Feedback — What | 0:55 | 5:35 |
| 8 | You Control It | 0:50 | 6:25 |
| 9 | What Happened — With Caveats | 1:30 | 7:55 |
| 10 | Where I'd Go Next | 0:05 | 8:00 |

Slide 9 now carries three beats (decay / split / revision window). It is the densest slide
in the deck and it earns the time — but rehearse it against a clock, because if it runs long
there is nothing left to give.

**The Classroom note (slide 3) is new and costs ~10s.** The title in the program says
"GitHub Classroom," so say it out loud before someone in the room does:

> "The title says GitHub Classroom. That's being retired — so distribution now runs on a
> small `gh` extension I wrote. Everything downstream is unchanged, which is rather the point."

Deliver it in one breath while advancing; don't stop on it. If you're behind at slide 3,
cut it entirely — it survives fine as an answer to a question, and the deck no longer
claims Classroom anywhere except the title.

## Checkpoints

- **2:40 leaving Codespaces.** If past 3:15, cut the callout-box example — say "structured template, renders to HTML and PDF" and move.
- **4:40 leaving the How slide.** Protect this one. If behind, compress slide 8 to one sentence: "You write the rubric in Markdown, the AI applies it."
- **Slide 9 gets the most time on purpose.** It's the only original data in the talk. If you're at 7:00 arriving, drop the decay detail but keep the 65% and the 15/13/15 split.

## Register

This is an experience report. You built the plane while flying it, and the talk says so
twice on purpose — once on slide 2, once on slide 9. That framing is doing real work: it
sets expectations so nobody arrives at slide 9 expecting a controlled study, and it makes
the numbers *interesting* rather than *contestable*. Don't apologize for it beyond those
two mentions — stated once plainly, it reads as confidence, not hedging.

The numbers are texture, not evidence. "Most tried it," "tailed off," "fifteen made it a habit"
— that register is right. Avoid effect sizes and normalized rates out loud; they promise
rigor the design can't back.

## The two things not to rush

**Slide 7** (the feedback screenshot) — the only moment the audience sees actual output. Beat of silence, then the "not 'good job'" line.

**Slide 9** — land the 65% and the tail-off, then say plainly you don't know why and didn't ask. That's the most honest moment in the talk and it's what makes the rest credible.

## Numbers — say these consistently

Your submitted abstract says "in under minutes," the INAAPT deck said "under 15 seconds," the README says both "10–15 seconds" and "1–3 minutes." Pick one and hold it:

> **"About 10–15 seconds of analysis; a minute or two wall-clock once the Action spins up."**

Data on slide 9, from the GitHub API (2026-07-18) joined to Brightspace exports.
Three Spring 2026 orgs: `202520-PHYS-280`, `202520-PHYS-230`, `202520-EENG-340`.

- **43 students, 440 repos, 191 feedback requests**
- **65% of students used it at least once**; ~26% of individual repos
- **15 never / 13 tried once or twice / 15 habitual (3+)**
- Rosters verified against gradebook: PHYS-230 24, PHYS-280 13, EENG-340 6

**Decay — requests / repos released that month:**

| | Jan | Feb | Mar | Apr |
|---|---|---|---|---|
| **per repo** | **0.61** | **0.51** | **0.38** | **0.22** |

**Revision (backup slide 2) — 627 Notability grading files.** Two separate questions:

*Did they revise?* Flat — 36.7% / 43.4% / 35.5% across 0 / 1-2 / 3+ requests.
Everyone took the end-of-term window at about the same rate.

*How much revision did it take?* Not flat:

| requests | revised items | needed a 2nd pass |
|---|---|---|
| 0 | 55 | 16% (9) |
| 1-2 | 61 | 3% (2) |
| 3+ | 56 | **0% (0)** |

Consistent with the feedback front-loading the fixes. Counted by *distinct submission
date*, not file count — batch re-runs (`may1` vs `may3` on the same date) and two Drive
duplicate files would otherwise have overcounted. Deduping made the gradient stronger,
not weaker.

Hold the caveats: 9 / 2 / 0 items is small, and careful students both seek feedback and
revise efficiently. "Suggestive" is the right word. Don't say "shows" or "proves." 

**Grades (backup slide 3) — all 42 usernames matched to gradebook:**

| requests | n | submitted | score when submitted |
|---|---|---|---|
| 0 | 15 | 78% | 92% |
| 1-2 | 12 | 86% | 95% |
| 3+ | 15 | 96% | 97% |

The raw report-average gap is ~18 points; nearly all of it is submission rate.
Conditional on submitting, ~5 points, near ceiling. Say "engaged students used it,"
not "it improved scores."

**Exclusions — know these cold:**

- An **instructor account** — not a student
- A **student-assistant account** — not enrolled in any of the three courses
- These two accounted for ~50 of January's requests. Removing them flattened the early
  decay curve considerably (Jan went 0.90 -> 0.61). If anyone asks whether early
  enthusiasm was real: partly it was staff.
- **One student dropped PHYS-280 mid-semester**; retained in the denominator (excluding
  them moves adoption 65% -> 64%, so keeping them is the conservative choice)
- **EENG-405** — one student, independent study
- **EENG-320 (Fall 2025)** — a *push* model: I generated and posted feedback on my own
  schedule. Spring is student-initiated. Different question; backup slide 1 covers it.

## Likely questions

**"Does it actually improve student work?"** — *You will get this one.* Go to **backup slide 3**. Say: I checked against gradebook scores. Students who used it scored higher, but almost all of that gap is submission rate — they turned more things in. Conditional on submitting, the difference is about five points near ceiling. So engaged students used it; I can't tell you the tool produced the engagement. A real answer needs it required in one section, unavailable in another, graded blind.

**"Is 65% good or bad?"** — Better than I expected for a purely optional tool, and it reframes the problem: the issue isn't getting students to try it, it's getting them to come back. Fifteen made it a habit, thirteen tried it and drifted. That middle thirteen is the group worth designing for.

**"Why did usage decay?"** — Don't overclaim; you have the curve, not the cause. Candidates worth naming: novelty wearing off; friction (it was a shell command, and tagging through the web UI is clunky); reports getting harder late in the term so students triage; or students deciding the feedback wasn't worth the round-trip. You can distinguish these next term by asking them — which you haven't done, and should say so.

**"Did the feedback change what students did?"** — Two answers, and the distinction matters. Whether they revised: no difference, everyone took the end-of-term window at about the same rate. How much revision they needed: students who never used feedback needed a second pass 16% of the time; heavy users, zero of 56. Consistent with the feedback front-loading fixes. Small numbers and self-selected, so suggestive rather than shown. Backup slide 2.

**"Did you ask students why?"** — No. That's the obvious gap and the honest answer. A three-question exit survey would have been worth more than any of this API archaeology.

**"How do you know the AI isn't hallucinating?"** — It's formative, never summative; it doesn't set a grade. Criterion-by-criterion with a narrow context window keeps it anchored to what's in the document.

**"Do students just write for the AI?"** — Partly, by design — the rubric *is* the target. The risk is optimizing for the rubric's letter over the physics. Worth naming, not dodging.

**"Isn't GitHub Classroom going away?"** — *Now likely, since the title says Classroom.* Yes. It mattered less than I expected: Classroom was only doing distribution — make a repo per student from a template, add them as a collaborator. That's a few `gh` API calls, so I wrote a `gh` extension that does it (`UINDY-INSTRUCTORS/gh-rba`, org-per-course, roster file, one command per assignment). Codespaces, Quarto, and the feedback Action never knew Classroom existed. If you're starting now, don't build on Classroom.

**"Students with no programming background?"** — Codespaces. The environment is the part that usually stops them, and it's gone.

**"Is it really free?"** — Yes with GitHub Education: Codespaces hours, Actions minutes, GitHub Models all covered. 5,000 model requests/hour on the enterprise tier, far above what a class generates.

**"Non-physics course?"** — Nothing is physics-specific; rubric and guidance are just Markdown.

## Cold open (optional)

Only if it's true of an actual student — don't invent it:

> "Last term a student pushed a lab report at 11 PM, got feedback in about a minute, fixed two things, and pushed again before midnight. I hadn't looked at it yet. That's the whole talk — let me show you how it's wired."

Given 30% of requests land between 8pm and 4am, something close to this almost certainly happened. But check before you claim a specific one.
