@.github/copilot-instructions.md

## Claude Code

This repo's canonical instructions live in `.github/copilot-instructions.md`
(imported above) so Copilot and Claude share one source of truth.

`lang-tutor` is the learner-facing half of the language-learning split: it owns
the exercises, per-user progress, the tutor LLM chain, and the webapp, and
depends on `lang-tools` (a sibling repo at `../lang-tools`) as a library for
content. The dependency is strictly one-way.
