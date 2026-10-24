@.github/copilot-instructions.md

## Claude Code

This repo's canonical instructions live in `.github/copilot-instructions.md`
(imported above) so Copilot and Claude share one source of truth.

`lang-tutor` is the learner-facing half of the language-learning split: it owns
the exercises, per-user progress, the tutor LLM chain, and the webapp, and
depends on `lang-tools`, pinned by git tag, as a library for content
(`make dev-lang-tools` swaps in a local `../lang-tools` checkout). The dependency
is strictly one-way.

Planning for this repo lives in `lang-tools`' `scratch_space/`: `08_lang_tutor/` for the
split, and `09_concept_model/tracking.md` first for current work.
