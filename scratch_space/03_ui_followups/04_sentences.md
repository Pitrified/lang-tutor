---
status: discarded
---

# Phase 4 - sentences for pt, es and fr

Deferred on 2026-11-03 (`00_start.md` Q6): the pt, es and fr sentences are not written in this folder.
The plan below stays as the starting point for a later folder.

## Overview

Sentence reconstruction needs example sentences, and pt, es and fr have 3 or 4 each. The
sentences are lang-tools data (`data/curated/example_sentences.jsonl`, applied at build, kept to
the lemma they use by `CardQuery.example_mentions_lemma`). Context: [`00_start.md`](00_start.md),
item 4; the source is `00_start.md` Q6.

## Plan

- From the source chosen in Q6, write sentences for the common A1-B1 lemmas of pt, es and fr
  into the curated file.
- A paid LLM run only after a measured sample and explicit approval.
- Rebuild the corpus, play sentence reconstruction in the three languages.

## Out of scope

- New exercise types.

## Done when

- Sentence reconstruction plays several distinct rounds in pt, es and fr.
- lang-tools `make check` passes and its quality gate reads PASS.
