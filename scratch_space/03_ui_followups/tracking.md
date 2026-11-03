# UI follow-ups - implementation tracking

The learner-side items left open after lang-tools' concept model and look-alike review: play the
look-alike drills on the reviewed corpus, fix the first cards, and fix a lang-tools import, in
one lang-tools release. Items, analysis and open
questions in [`00_start.md`](00_start.md).

## Key decisions

- The folder runs phases 1, 3 and 5; durable progress (phase 2) and pt/es/fr sentences (phase 4)
  are deferred (`00_start.md` Q4, Q6).
- Every lang-tools code change waits for one release and one pin bump in phase 5; data changes
  reach lang-tutor through the read API without a tag.
- This folder owns the look-alike end-to-end check (`00_start.md` Q3).

## Phases

| #  | Phase                  | Plan                                               | Status |
| -- | ---------------------- | -------------------------------------------------- | ------ |
| 1  | Look-alike drills      | [`01_lookalike_drills.md`](01_lookalike_drills.md) | done |
| 2  | Durable progress       | [`02_durable_progress.md`](02_durable_progress.md) | discarded |
| 3  | First cards            | [`03_first_cards.md`](03_first_cards.md)           | planned |
| 4  | Sentences for pt/es/fr | [`04_sentences.md`](04_sentences.md)               | discarded |
| 5  | lang-tools release     | [`05_lang_tools_release.md`](05_lang_tools_release.md) | planned |

Status values: draft / planned / in progress / done / superseded / discarded.

## Log

Append-only. Newest at the bottom.

- 2026-11-03 : opened the folder on branch `feat/03_ui_followups`, from the open items in
  lang-tools' `09_concept_model` backlog and `11_lookalike_review` phase 5. Five draft phases;
  questions Q1 to Q7 raised in `00_start.md`.
- 2026-11-03 : Q1 to Q7 answered. Planning location moved here in `CLAUDE.md` and
  `.github/copilot-instructions.md` (Q1); order kept (Q2); this folder owns the look-alike check,
  and lang-tools' `11_lookalike_review/05_closeout.md` now names it (Q3); durable progress and
  sentences deferred, phases 2 and 4 marked discarded here (Q4, Q6); first cards measured first
  (Q5); the import fix is a lazy `WebappParams` import (Q7). Phases 1, 3, 5 planned.
- 2026-11-03 : phase 1 started. Plan review: `draw_cards` samples a random window over the whole
  query pool, not the frequent cards first, so the trap share follows the pool's trap rate;
  decoys need a trap in the right column's language. Both written into `01_lookalike_drills.md`.
- 2026-11-03 : phase 1 played and measured on the 2026-10-31 corpus (300 rounds per setting):
  traps are about 11% of the pt B1 pool and 13-16% of the paired cards, so the 1.3 trap bonus
  does not over-select, and the weights stay. Three findings raised: partial false friends make
  wrong decoys (Q8), the tier A notes are too terse to explain a mistake (Q9), and the look-alike
  review's phase 3 samples were never built into the corpus (Q10). Bad translations seen in play
  added to phase 3.
- 2026-11-03 : Q8 to Q10 answered (a, b, a). Decoys now come only from full false friends; a
  second check, against the card's own translations, was tried for the *era* case and dropped
  (it fired on 0 of 1,942 cards), and *era* moved to phase 3 as a best-sense problem. The
  lang-tools corpus was rebuilt with the look-alike review's phase 3 samples: 6,852 edges, gate
  PASS. The terse notes went to lang-tools as `r0011`. `make check` green (148). Phase 1 closed.
