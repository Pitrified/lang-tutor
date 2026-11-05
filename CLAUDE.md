@.github/copilot-instructions.md

## Claude Code

This repo's canonical instructions live in `.github/copilot-instructions.md`
(imported above) so Copilot and Claude share one source of truth.

`lang-tutor` is the learner-facing half of the language-learning split: it owns
the exercises, per-user progress, the tutor LLM chain, and the webapp, and
depends on `lang-tools`, pinned by git tag, as a library for content
(`make dev-lang-tools` swaps in a local `../lang-tools` checkout). The dependency
is strictly one-way.

Planning for this repo lives in its `scratch_space/`, one numbered folder per initiative,
`tracking.md` first. The earlier planning (the repo split, the concept model) is in
`lang-tools`' `scratch_space/`.
