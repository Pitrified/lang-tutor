---
status: in progress
priority: 0
description: |
  The learner-side follow-ups left open after lang-tools' concept model and look-alike review:
  play the look-alike drills on the reviewed corpus, fix the first cards a learner meets, and
  fix a lang-tools import, in one lang-tools release.
comment: |
  Opened on 2026-11-03, on the user's request to go back to the UI and go through every open
  item touching lang-tutor. The items come from lang-tools' 09_concept_model backlog and from
  phase 5 of 11_lookalike_review (both in the lang-tools repo). Durable progress and pt/es/fr
  sentences were deferred (Q4, Q6).
---

# UI follow-ups - start

## The idea

After the look-alike review, go back to the learner-facing app and go through every open item
that touches it, in the user's words: "now we go back to some ui... open a plan folder in tutor,
let's go through all of them".

## Where lang-tutor stands

- On `main` at `d6930c5`, clean, pinned to `lang-tools @ v0.2.0`.
- The five exercises play end to end over HTTP in pt, en and fr (lang-tools `09_concept_model`
  phase 9). Rounds are drawn from `LemmaCard`s weighted by session progress
  (`progress/selection.py`).
- The look-alike surface is built:
  - pair matching can use a false friend as a decoy and returns the trap note when it fools the
    learner (`exercises/pair_matching.py`);
  - selection multiplies a trap's weight by 1.3 and a cognate's by 0.7 (`SelectionWeights`);
  - the lemma page lists the best sense's traps and cognates (`routers/lemmas_router.py`).
- It was last played on a corpus of about 2,800 look-alike edges. The rebuilt corpus in
  lang-tools now has 5,523 (4,768 cognate, 356 partial, 399 full), and phase 4 of the review
  (tiers C and D) will add more.
- Since `v0.2.0`, lang-tools changed data, docs and plans; the only `src/` change is to the
  quality report. Reviewed data reaches lang-tutor through the read API or a local checkout,
  never through the tag, so the new edges need no pin bump.

## The open items

1. **Look-alike drills on the reviewed corpus.** Serve the rebuilt corpus, play pair matching
   and the lemma pages, and check:
   - that the trap note reads well after a wrong tap;
   - whether the 1.3 trap bonus now over-selects, since tier B put traps among the most
     common cards.
   Source: lang-tools `11_lookalike_review/05_closeout.md`.
2. **Progress lost on restart.** `SessionProgressService` keeps every `UserLemmaProgress` in
   memory per process, and its docstring names itself the seam a durable store replaces. Users
   are in memory too (`UserService`). The Render blueprint runs on the free plan, which has no
   persistent disk. Source: lang-tools `09_concept_model/09_sample_and_consumer.md` Q2.
3. **Bad first cards.** Common inflected forms get a rare homograph as their best sense: pt *é*
   "e" (the letter), *são* "healthy", *seja* "are", and *brasil* "brazilwood". The best sense is
   the highest `sense_frequency`, with ties broken by concept commonness
   (lang-tools `lemma_store._derive_drill_table`), so a sense with no frequency data can win.
   The fix is in lang-tools: a curated override for the top forms (data), or a rule in the
   best-sense pick (code, so a tag and a pin bump). Source: lang-tools `09_concept_model`
   backlog.
4. **Sentence reconstruction has almost no content.** OMW has example sentences for en and it
   only; pt, es and fr have 3 or 4 each, from 10 hand-written rows in lang-tools
   `data/curated/example_sentences.jsonl`. Two ways to scale it, both in lang-tools: an LLM job
   on the phase 8 loop (paid, sample-measured first), or Tatoeba (CC-BY, already staged).
   Source: lang-tools `09_concept_model` backlog and `09_sample_and_consumer.md` Q1.
5. **`lang_tools.lexicon` needs fastapi-tools to import.** `lemma_store` imports the params,
   which import `WebappParams`, which imports `fastapi_tools`, but fastapi-tools is only in
   lang-tools' `webapp` extra. lang-tutor does not hit it, since `make sync` installs every
   extra. The fix is lang-tools code: a patch release and a pin bump. Source: lang-tools
   `09_concept_model` backlog.

Related but not in this folder: data for tag installs (lang-tools `10_data_for_tag_installs`),
which only matters for the `in_process` mode, and has an answer for now
(`make dev-lang-tools`).

## Proposed phases

Cheapest and most informative first:

1. Look-alike drills check: no paid run, no code unless the check finds something.
2. Durable progress: lang-tutor only.
3. First cards: lang-tools data or code, measured first.
4. Sentences for pt, es, fr: lang-tools data, the only item that may cost money.
5. lang-tools release: the import fix, plus any code change from phase 3, in one tag and one
   pin bump.

Settled on 2026-11-03 (Q2, Q4, Q6): the order holds, and phases 2 and 4 are deferred, so the
folder runs 1, 3, 5. Their files stay, marked `discarded` for this folder, as the starting point
for a later folder.

## Open questions

- Q1: This folder sits in lang-tutor's `scratch_space/`, but both `CLAUDE.md` and
  `.github/copilot-instructions.md` say planning for this repo lives in lang-tools' `scratch_space/`.
  - a. Update both files: lang-tutor plans live here from `03_ui_followups` on, and the earlier
    ones stay in lang-tools.
  - b. Leave the files as they are and treat this folder as an exception.
  - Recommended: a, because otherwise the next session reads the instructions and looks for this
    plan in the wrong repo.
  - ANS: a. Both files updated on 2026-11-03:
    plans for this repo live here, and the earlier ones stay in lang-tools.
- Q2: Phase order.
  - a. As proposed: drills check, progress, first cards, sentences, release.
  - b. First cards first: they are the first thing a learner sees, and the drills check would
    then run on better cards.
  - Recommended: a, because the drills check costs nothing and can change the selection weights
    that phase 3 then measures against.
  - ANS: a. Drills check, then first cards, then the release;
    phases 2 and 4 are deferred (Q4, Q6).
- Q3: The drills check overlaps lang-tools `11_lookalike_review/05_closeout.md`, which lists the
  same end-to-end check.
  - a. This folder owns the check, and the look-alike close-out names this folder for it and
    keeps its own two items (overlap cognates, seed re-export).
  - b. The look-alike close-out keeps it, and this folder drops phase 1.
  - Recommended: a, because the check is played in lang-tutor and its fixes (weights, the trap
    note) land here.
  - ANS: a. This folder owns the check.
    lang-tools' `11_lookalike_review/05_closeout.md` now names it,
    and re-runs it only if tiers C and D change the result.
- Q4: Where durable progress is stored, given that Render's free plan has no persistent disk.
  - a. One SQLite file under lang-tutor's `data/`, behind the `SessionProgressService` seam;
    durable locally, and lost on a Render redeploy until a disk or a database is added.
  - b. A JSON file per user, same seam, same Render caveat.
  - c. A hosted database now (Render Postgres or similar), which also covers users.
  - Recommended: a, because it fixes local use at once, keeps one file and one query
    language, and moves to a hosted database later behind the same seam.
  - ANS: Not now: the permanent store is deferred.
    Phase 2 is set aside, and progress stays in memory.
- Q5: How to fix the bad first cards.
  - a. A rule in lang-tools' best-sense pick: a sense with no frequency data cannot become the
    best sense of a common lemma (code: tag and pin bump).
  - b. A curated override of the best sense for the top forms (data only, no tag).
  - c. Measure first: count how many of the 500 most common pt, es and fr cards have a junk best
    sense, then choose between a and b.
  - Recommended: c, because a query against the corpus is cheap and the count decides whether a
    hand list is enough.
  - ANS: c. Phase 3 counts the junk best senses first, then picks a rule or an override.
- Q6: Where pt, es and fr sentences come from.
  - a. Tatoeba: real sentences, free, already staged; CC-BY, so attribution goes in the dataset
    card, and quality and level vary.
  - b. An LLM job on the phase 8 loop, one A1-B1 sentence per lemma, sample-measured and
    approved before the paid run.
  - c. Tatoeba first, then the LLM job for the common lemmas Tatoeba does not cover.
  - Recommended: c, because Tatoeba is free and real, and the paid job then only covers the gap.
  - ANS: Deferred.
    Phase 4 is set aside; sentence reconstruction keeps its 3 or 4 sentences in pt, es and fr.
- Q7: How to fix the fastapi-tools import in lang-tools.
  - a. Import `WebappParams` lazily, so the lexicon imports without the `webapp` extra.
  - b. Make fastapi-tools a base dependency of lang-tools.
  - Recommended: a, because the lexicon has no use for the webapp, and b would pull a web stack
    into every content consumer.
  - ANS: a. Phase 5 imports `WebappParams` lazily.
- Q8: Pair matching uses partial false friends as decoys, so a right answer can be marked
  wrong (pt *era* / en *era*: the note itself says pt *era* is "also an era"). Found in phase 1.
  - a. Decoys only from full false friends (`kind == "full"`); partials keep the selection
    bonus and the lemma page note. One condition in `PairMatchingExercise._decoys`, plus a test.
  - b. Keep partial decoys, and count a tap on one as correct, with the note as a hint.
  - c. Keep as is.
  - Recommended: a, because a decoy has to be wrong to work, and a partial is right in some
    sense; full false friends are 399 of the 755 served traps, so about half the decoys stay.
  - ANS: a. Decoys only from full false friends, in `PairMatchingExercise._decoys`, with a
    test. It does not cover the *era* case that raised the question: that edge is `full` (the
    rulebook's own example, by the inflected-form rule), and the card teaches *era*'s noun
    sense, "an indefinite period", whose only en lemma is *time*. So a check against the
    card's own translations would not catch it either; tried and dropped, since it fired on 0
    of 1,942 cards. The *era* case is a best-sense problem and goes to phase 3.
- Q9: The trap notes come in two styles: tier A's terse (`pt: pull`, often the pt side only) and
  tier B's full (`pt "fato" means fact; en "fate" is "destino"`). After "False friend!" a terse
  note does not say what the tapped word means. The notes are lang-tools data. Found in phase 1.
  - a. Leave the notes; show the note on the lemma page only, and after a wrong tap show the pt
    word's own translation next to it.
  - b. Rewrite the terse notes to the full style in lang-tools, as a `recheck` of those trap
    rows under a rulebook line on the note format: 139 of the 755 served trap notes (87 full,
    52 partial) are terse, so one agent batch.
  - c. Leave it for now.
  - Recommended: b, because the note is what a learner reads at the moment of the mistake, and
    the review machinery already does exactly this; it belongs in lang-tools'
    `11_lookalike_review`, not here.
  - ANS: b. The current rulebook's Notes section already asks for both sides, and the terse rows
    predate it, so lang-tools' `11_lookalike_review/04_tiers_c_to_e.md` now opens with an `r0011`
    re-check of the 139 rows, with no guide change.
- Q10: The phase 3 samples of lang-tools' look-alike review (3,000 rows, about 1,280 cognates and
  71 traps) were committed after the last corpus build, so the served corpus lacks them
  (*prejudicar* / *prejudice*). Found in phase 1.
  - a. Rebuild the lang-tools corpus now (about 4 minutes, then the quality gate, which
    rewrites the tracked `report.md`, and a commit of it on lang-tools `main`).
  - b. Leave it to the next look-alike round (phase 4 of `11_lookalike_review`), which rebuilds
    after every round anyway.
  - Recommended: b, because the missing rows are mostly cognates of rarer words and do not
    change this phase's numbers, and the next review round rebuilds anyway.
  - ANS: a. Corpus rebuilt on 2026-11-03.
- Q11: Phase 3's count found about 98 bad cards in the pt top 500 (a third of the top 100), from
  four causes (`03_first_cards.md`, "What the implementation found"). Which fixes go in?
  1. One-letter lemmas get no card: a rule in lang-tools' drill table (code).
  2. Translations put a word before a digit, a Roman numeral or a single letter (*dez* "ten",
     not "x"): a rule in lang-tools' card translations (code).
  3. Drop the wrong links (*seja* "are", *tinha* "ringworm", fr *a* "repel") as reviewed rows
     in the existing `member_form_drops.jsonl` (data).
  4. A new reviewed best-sense override, so a lemma whose right sense loses the pick shows it
     (*homens* "men", *bem* "well"): a new curated file and its applier (code), plus the rows.
  - a. All four. The review for 3 and 4 runs on the top 1,000 cards per language with the
    agent harness of the look-alike review (a rulebook and a CLI subcommand), as its own
    lang-tools folder; this phase then re-lists the cards.
  - b. 1, 2 and 3 only: no new applier, and the "loses the pick" group (about 43 per 500 in
    pt, the largest) stays.
  - c. 1 and 2 now, which fix about 26 of the 98 in pt; 3 and 4 move to their own lang-tools
    folder, and this phase closes on the rules.
  - Recommended: a, because the largest group needs 4, and the review machinery exists; c is
    the fallback if a new review is too much right now.
  - ANS: a. All four go in lang-tools' `12_card_senses` (branch `feat/12_card_senses`), opened
    on 2026-11-03: phase 1 the two rules, phases 2 to 4 the override input, the review harness
    and the run. This folder's phase 3 waits for it, then re-lists the cards; its code ships in
    phase 5's release.
- Q12: The pt *era* card now teaches the noun "era" (lang-tools `12_card_senses` pinned it),
  but its look-alike with en *era* is labelled `full` (lang-tools look-alike recheck `r0001`
  changed it from `partial`: the frequent reading is "was"). Pair matching takes every `full`
  look-alike as a decoy, so a round can offer "era" as the wrong answer for a card meaning era.
  It is the only such case in the top 1,000 pt cards.
  - a. Relabel the pair `partial` in lang-tools with a later row in `lookalikes.jsonl` (latest
    row wins), noting the card: no decoy, and the lemma page still warns about "was".
  - b. In lang-tutor, skip a decoy whose text the card's gloss or translations contain. It
    misses *era* itself (its translations are "age, historic period") unless the gloss is
    searched, and the gloss search gives false hits (*novela* "novel").
  - c. Leave it: one card, and the trap note still teaches "was".
  - Recommended: a, because the label is wrong for the card that is shown, and the data fix
    is one row.
  - ANS: a. Relabelled `partial` in lang-tools `lookalikes.jsonl` with a later row
    (`model` `manual`, batch `correction`), keeping the note batch `a0001` wrote.
