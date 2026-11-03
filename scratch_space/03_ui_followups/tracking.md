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
| 1  | Look-alike drills      | [`01_lookalike_drills.md`](01_lookalike_drills.md) | planned |
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
