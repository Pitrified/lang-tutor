---
status: done
---

# Phase 1 - look-alike drills on the reviewed corpus

## Overview

Play the look-alike surface on the corpus the review rebuilt (5,523 edges) and fix what the play
shows. Context: [`00_start.md`](00_start.md), item 1. This folder owns the check (`00_start.md` Q3);
lang-tools' `11_lookalike_review` close-out re-runs it only if tiers C and D change the result.

## Plan

- Serve the rebuilt lang-tools corpus (`make serve` in lang-tools, port 8010) and run lang-tutor
  in dev mode (`make serve`), content source `http`.
- Play pair matching in pt with en and it as known languages, and open the lemma pages of a few
  reviewed traps (*esquisito*, *prejudicar*, *simpática*) and cognates.
- Measure the trap share of drawn rounds: draw a few hundred rounds through `draw_cards` in a
  scratch script, and compare the share of traps against the share in the candidate window.
  `draw_cards` samples its window at random over every card the query allows (pt, single word,
  B1 or easier, with an en translation), not the most frequent first, so the window's trap share
  is the pool's; the 1.3 bonus moves the drawn share above it.
- Count the rounds that get a decoy. A decoy needs a trap in the right column's language (en by
  default), so it traps only show as decoys when the right column is it.
- Check the trap note's wording after a wrong tap, and partial against full false friends.
- Fix what the play finds: `SelectionWeights.trap_factor`, the note text, the lemma page.

## Out of scope

- New look-alike data: phase 4 of lang-tools `11_lookalike_review`.

## Done when

- The drills are played on the rebuilt corpus, and the findings are written below.
- The trap share is measured, and the weights changed or kept with the reason.
- `make check` passes in lang-tutor.

## What the implementation found

Played on 2026-11-03 against the corpus built on 2026-10-31 (5,523 edges), lang-tools read API
on port 8010, lang-tutor in dev mode on port 8000. The measurement replays the pair-matching
endpoint (same query, `select_lemmas`, `PairMatchingExercise.start` with 5 pairs, 3 spares and
1 decoy) for a fresh learner, 300 rounds per setting.

| Right column | Trap factor | Traps in the window | Traps among paired cards | Rounds with a trap | Rounds with a decoy |
| ------------ | ----------: | ------------------: | -----------------------: | -----------------: | ------------------: |
| en | 1.0 | 11.2% | 13.1% | 54% | 33% |
| en | 1.3 | 10.4% | 13.2% | 50% | 31% |
| it | 1.0 | 11.3% | 12.7% | 47% | 30% |
| it | 1.3 | 11.0% | 16.0% | 59% | 34% |

- **The trap bonus does not over-select.** About 11% of the pt B1 pool are traps, and 13-16% of
  the paired cards. Most of the lift comes from the 0.7 cognate damping (cognates are 44% of
  the pool), not from the 1.3 trap bonus, whose effect is within noise on en (about ±1.7 points
  on 1,500 paired cards). Weights kept.
- **Partial false friends make wrong decoys.** A decoy is any trap, partial included, so a
  correct answer can be marked wrong. Played live: the round paired *era* with *time*, put en
  *era* in the column as a decoy, and tapping *era* / *era* returned "False friend! pt "era" is
  mostly "was" (ser), also an era". The same holds for *forte* / *fort*, *assistir* / *assist*,
  *importar* / *import*, *particular* / *particular*, *logo* / *logo*, *solo* / *solo*.
  Raised as `00_start.md` Q8.
- **The notes come in two styles.** The tier A notes are terse (`pt: pull`, `pt: date`,
  `pt: take off, remove`) and often name only the pt side; the tier B notes name both sides
  (`pt "fato" means fact; en "fate" is "destino"`). A terse note after "False friend!" does not
  say what the tapped word means. 139 of the 755 served trap notes (87 full, 52 partial) are
  terse. The notes are lang-tools data. Raised as `00_start.md` Q9.
- **The lemma page reads well.** *esquisito* shows "false friend en exquisite - pt: weird, odd";
  *forte* shows the partial false friend with its note and the two cognates.
- **The phase 3 samples of the look-alike review are not in the served corpus.** Their 3,000
  rows (about 1,280 cognates and 71 traps in tiers C to E, among them *prejudicar* /
  *prejudice*) were committed after the last build, so *prejudicar* shows no look-alike. A
  rebuild folds them in. Raised as `00_start.md` Q10.
- **Translations, for phase 3:** the same live round paired *postar* with "get off" and
  *primeira* with "prime", which belong with the first-card measurement in
  [`03_first_cards.md`](03_first_cards.md).

### Fixes, 2026-11-03

- **Decoys** (`00_start.md` Q8, a): only a full false friend becomes a decoy
  (`PairMatchingExercise._decoys`, test `test_partial_false_friend_is_no_decoy`, and
  `docs/guides/content_source.md`). This removes the *forte*, *assistir* and *importar* kind
  of decoy, not the *era* one, which is a best-sense problem moved to phase 3.
- **Corpus rebuilt** (Q10, a): 6,852 edges (6,046 cognate, 388 partial, 418 full; +1,329
  against 5,523, the phase 3 samples), 257 rare-word traps dropped, 6 stale, gate PASS, seed
  unchanged. *prejudicar* now carries *prejudice*. Of 1,942 distinct cards in 150 windows,
  63 have an en full false friend.
- **Terse notes** (Q9, b): moved to lang-tools' `11_lookalike_review` as `r0011`.
