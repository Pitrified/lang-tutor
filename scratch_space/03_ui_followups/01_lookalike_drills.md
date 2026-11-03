---
status: planned
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
  scratch notebook, and compare the share of traps against the share in the candidate window.
- Check the trap note's wording after a wrong tap, and partial against full false friends.
- Fix what the play finds: `SelectionWeights.trap_factor`, the note text, the lemma page.

## Out of scope

- New look-alike data: phase 4 of lang-tools `11_lookalike_review`.

## Done when

- The drills are played on the rebuilt corpus, and the findings are written below.
- The trap share is measured, and the weights changed or kept with the reason.
- `make check` passes in lang-tutor.
