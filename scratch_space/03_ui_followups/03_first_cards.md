---
status: planned
---

# Phase 3 - first cards

## Overview

The most common cards are the first a learner meets, and some show a rare homograph: pt *é* "e",
*são* "healthy", *seja* "are", *brasil* "brazilwood". The fix is in lang-tools. Context:
[`00_start.md`](00_start.md), item 3; measure first, then choose (`00_start.md` Q5, c).

## Plan

- Measure: list the 500 most common pt, es and fr cards with their best sense, and count those
  whose best sense has no frequency data or reads as junk.
- Choose from the count, and record the choice here:
  - a few hand-picked forms: a curated best-sense override applied at build (data, no tag);
  - many, sharing a cause: a rule in `lemma_store._derive_drill_table` (code, released in
    phase 5).
- Fix by the chosen method.
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
