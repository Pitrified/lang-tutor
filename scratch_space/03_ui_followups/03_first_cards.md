---
status: in progress
---

# Phase 3 - first cards

## Overview

The most common words show a rare homograph as their meaning: pt *é* "e", *são* "healthy",
*seja* "are", *brasil* "brazilwood". Rounds draw at random over the whole B1 pool, so these are
not literally the first cards a learner meets, but they are the words met most often, on every
exercise and lemma page. The fix is in lang-tools. Context:
[`00_start.md`](00_start.md), item 3; measure first, then choose (`00_start.md` Q5, c).

## Plan

- Measure: list the 500 most common pt, es and fr cards with their best sense, and count those
  whose best sense has no frequency data or reads as junk.
- Sort the bad cards by cause, since one rule cannot fix them all: the right sense exists but
  loses the pick (pt ties on frequency and falls back to concept commonness); the lemma has no
  right sense at all (*é* is only the letter); or the sense is right and the translation is
  wrong.
- Choose from the count, and record the choice here:
  - a few hand-picked forms: a curated best-sense override applied at build (data, no tag);
  - many, sharing a cause: a rule in `lemma_store._derive_drill_table` (code, released in
    phase 5).
- Fix by the chosen method. Chosen on 2026-11-03 (`00_start.md` Q11, a): all four causes are
  fixed in lang-tools' `12_card_senses`; this phase waits for it.
- Rebuild the lang-tools corpus and re-list the same cards.
- Include the translation the card shows: phase 1 played *postar* paired with "get off" and
  *primeira* with "prime".
- Include the inflected forms labelled `f` by their frequent reading whose card teaches the
  other, shared sense: pt *era* is labelled `f` against en *era* as "was", but its card shows
  "an indefinite period" (*time*), so pair matching can offer en *era* as a decoy for a card on
  the era sense (phase 1, `00_start.md` Q8).

## Out of scope

- Senses missing from OMW (pt *eventualmente*): lang-tools' new-lemma mapping backlog item.

## Done when

- The re-listed top cards show no junk best sense, or the ones left are listed with the reason.
- lang-tools `make check` passes and its quality gate reads PASS.

## What the implementation found

The 500 most frequent single-word cards per language, with every sense, listed on 2026-11-03
from the rebuilt corpus (`CardQuery(order="frequency", single_word=True)`). pt read in full,
es and fr top 150 read, all three counted by script for the mechanical causes. The pt
counts by cause are my reading, so they are estimates:

| Cause | pt (of 500) | Examples | Mechanism today |
| ----- | ----------: | -------- | --------------- |
| One-letter lemma | 18 (es 8, fr 9, by script) | pt *d*, *c* "one hundred", es *x* "ecstasy", fr *g* "mobile phone" | none |
| No right sense: an inflected form or other word linked to a rare concept | about 25 | pt *seja* "are" (unit), *tinha* "ringworm", *deve* "debit", *olha* "bouillon", *veio* "axle", fr *a* "repel", *comment* "yak", *est* "east" | `member_form_drops.jsonl` (reviewed, applied at build) |
| Right sense exists but loses the pick | about 43 | pt *homens* "work force", *minutos* meeting minutes, *bem* "kind of", *ainda* "also", *tarde* "night", *regras* "menstruation", fr *un* "two", *hommes* "work force" | none |
| Sense right, first translation wrong | 8 by script (es 4, fr 11), plus *aí* / *lá* "yon" | pt *dez* "x", *dois* "2", fr *tel* "i", *dix* "10" | none |
| Lowercase proper noun | 1 | pt *brasil* "brazilwood" (es *argentina*, *china* "pebble", fr *louis*) | none |

- About 98 of the pt top 500 (20%) are wrong, and about a third of the top 100.
- The ties come from the best-sense pick: outside English every sense of a lemma ties on
  frequency, so concept commonness decides, and a common concept that the lemma only reaches
  through a rare reading wins (*homens* "work force").
- The closed-class list leaves out inflected verb forms on purpose (they are content words),
  and those are most of the "no right sense" group.
- The *era* case from phase 1 belongs to the "loses the pick" group in reverse: the noun sense
  is a real one, but the label is about the frequent reading "was".
- Q5 c asked for a count to choose between a rule and an override. The count says neither
  alone: the four causes need four fixes. Raised as `00_start.md` Q11.
