# Lang tutor

`lang-tutor` is the learner-facing tutoring and exercises app of the
language-learning ecosystem (Portuguese-focused, multi-language by design). It
owns the stateful, per-user experience:

- Five exercise mechanics: sentence reconstruction, pair matching, diacritic
  typing, wordle, and a conversational tutor.
- Per-user progress tracking and weighted card selection.
- An interactive tutor LLM chain (correction + conversation continuation).
- A FastAPI webapp (pages, runtime exercises API, Google OAuth, session state).

It depends on the companion [`lang-tools`](https://github.com/Pitrified/lang-tools)
repo for content: `LemmaCard` drill cards (with their false friends and
cognates), lemma and concept reads, `Language` presets, and content-producing
LLM chains. The dependency is one-way; `lang-tools` never imports `lang-tutor`.
Content comes over HTTP from the `lang-tools` read API by default, or in-process
from a local `lang-tools` checkout (see `docs/guides/content_source.md`).

## Installation

### Setup `uv`

To install the package:

Setup [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

### Install the package

Run the following command:

```bash
uv sync --all-extras --all-groups
```

## Docs

Docs are available at [https://pitrified.github.io/lang-tutor/](https://pitrified.github.io/lang-tutor/).

## Setup

### Environment Variables

To setup the package, create a `.env` file in `~/cred/lang-tutor/.env` with the following content:

```bash
LANG_TUTOR_SAMPLE_ENV_VAR=sample
```

And for VSCode to recognize the environment file, add the following line to the
workspace [settings file](.vscode/settings.json):

```json
"python.envFile": "/home/pmn/cred/lang-tutor/.env"
```

Note that the path to the `.env` file should be absolute.

### Pre-commit

To install the pre-commit hooks, run the following command:

```bash
uv run pre-commit install
```

Run against all the files:

```bash
uv run pre-commit run --all-files
```

`ruff` and `pyright` are pinned exactly and match the hook revs; bump both
together (see `docs/guides/pre_commit.md`).

### Linting

Use pyright for type checking:

```bash
uv run pyright
```

Use ruff for linting:

```bash
uv run ruff check --fix
uv run ruff format
```

### Testing

To run the tests, use the following command:

```bash
uv run pytest
```

or use the VSCode interface.

## Running the webapp

```bash
uvicorn lang_tutor.webapp.app:app --reload
```

In dev mode (`ENV_STAGE_TYPE=dev`, the default) Google OAuth is disabled and a
hardcoded dev user is injected, so the app runs with zero configuration.
