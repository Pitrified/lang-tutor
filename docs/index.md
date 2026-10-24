# Lang Tutor

Welcome to the **Lang Tutor** documentation.

`lang-tutor` is the learner-facing tutoring and exercises app of the
language-learning ecosystem (Portuguese-focused, multi-language by design). It
owns the stateful, per-user experience; vocabulary content comes from the
companion [`lang-tools`](https://github.com/Pitrified/lang-tools) library.

## Features

- **Exercises** - five mechanics: sentence reconstruction, pair matching,
  diacritic typing, wordle, and a conversational tutor.
- **Progress** - per-user `UserLemmaProgress` (in memory per session) and
  weighted selection over `lang-tools` drill cards (`LemmaCard`), drawn by CEFR
  level. Cards carry their look-alikes in the learner's known languages (false
  friends and cognates), which shape selection, pair-matching decoys, and the
  lemma page.
- **Tutor chain** - an `llm-core` `StructuredLLMChain` producing a correction
  plus a conversation continuation.
- **FastAPI webapp** - pages, runtime exercises API, Google OAuth (disabled in
  dev), session state, Jinja2 + HTMX.
- Python 3.14, managed with [uv](https://docs.astral.sh/uv/).
- Pre-configured Ruff, Pyright, pytest, pre-commit, and MkDocs.

## Quick Start

```bash
git clone https://github.com/Pitrified/lang-tutor.git
cd lang-tutor

make sync
make check
make docs
make serve
```

`lang-tools` is consumed as a library; for local development it is resolved via
an editable `[tool.uv.sources]` path to `../lang-tools`. Content is read over
HTTP from the `lang-tools` service by default, or in-process from that checkout
(see the content source guide).

## Project Structure

```
lang-tutor/
├── src/lang_tutor/       # Main package
│   ├── config/             # Pydantic config models
│   ├── data_models/        # BaseModelKwargs and shared models
│   ├── exercises/          # The five exercise mechanics + round/result protocol
│   ├── llm/                # Interactive tutor StructuredLLMChain
│   ├── metaclasses/        # Singleton metaclass
│   ├── params/             # Env-aware params and paths
│   ├── progress/           # Per-user progress + weighted selection
│   └── webapp/             # FastAPI app, routers, exercises API, auth, services
├── tests/                  # Test suite mirroring src/
├── docs/                   # MkDocs source (you are here)
└── scratch_space/          # Experimental notebooks and vibes
```

## Next Steps

- [Getting Started](getting-started.md) - Set up your development environment.
- [Guides](guides/uv.md) - Tooling and project conventions.
- [API Reference](reference/) - Auto-generated from docstrings.
- [Contributing](contributing.md) - How to contribute.
