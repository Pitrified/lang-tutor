# Lang Tutor

Welcome to the **Lang Tutor** documentation.

`lang-tutor` is the learner-facing tutoring and exercises app of the
language-learning ecosystem (Portuguese-focused, multi-language by design). It
owns the stateful, per-user experience; vocabulary content comes from the
companion [`lang-tools`](https://github.com/Pitrified/lang-tools) library.

## Features

- **Exercises** - five mechanics: sentence reconstruction, pair matching,
  diacritic typing, wordle, and a conversational tutor.
- **Progress** - per-user `UserLemmaProgress` and weighted lemma selection over
  the `lang-tools` lemma pool.
- **Tutor chain** - an `llm-core` `StructuredLLMChain` producing a correction
  plus a conversation continuation.
- **FastAPI webapp** - pages, runtime exercises API, Google OAuth (disabled in
  dev), session state, Jinja2 + HTMX.
- Modern Python 3.14, managed with [uv](https://docs.astral.sh/uv/).
- Pre-configured Ruff, Pyright, pytest, pre-commit, and MkDocs.

## Quick Start

```bash
git clone https://github.com/Pitrified/lang-tutor.git
cd lang-tutor

uv sync --all-extras --all-groups

uv run pytest
uv run mkdocs serve
uvicorn lang_tutor.webapp.app:app --reload
```

`lang-tools` is consumed as a library; for local development it is resolved via
an editable `[tool.uv.sources]` path to `../lang-tools`, and lemma content is
read from that checkout in-process.

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
