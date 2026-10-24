# lang-tutor - Copilot Instructions

## Project overview

`lang-tutor` is the **learner-facing** half of a language-learning ecosystem (Portuguese-focused,
multi-language by design): the five exercise mechanics, per-user progress and weighted card
selection, the interactive tutor chain, and the FastAPI webapp (pages, exercises API, Google
OAuth, session state). Python 3.14, managed with **uv**. Package `lang_tutor`.

## The lang-tools boundary - read this first

All vocabulary content comes from [`lang-tools`](https://github.com/Pitrified/lang-tools), pinned
by git tag in `pyproject.toml`: `LemmaCard` drill cards with their false friends and cognates,
`CardQuery`, lemma and concept reads, `Language` presets, and the content-producing LLM chains.
The surface you may use is `lang-tools`' `docs/library/frozen_api.md`.

**Do not model or store content here.** If an exercise needs a content field lang-tools does not
serve, add it there, cut a tag, and bump the pin. `lang-tools` must never import `lang-tutor`.

Content is read through the `lang_tutor.content` seam (`docs/guides/content_source.md`):

- `LANG_TOOLS_CONTENT_SOURCE=http` (default): the lang-tools read API at `LANG_TOOLS_BASE_URL`.
- `in_process`: the lang-tools store, reading the corpus under a local lang-tools checkout's
  `data/`. A tag install carries no data, so this mode needs `make dev-lang-tools`.

## AI code development

At the end of the overall task assigned by the user, instead of ending the conversation, always use
the #askQuestions tool to ask the user if they want to add more details, features, or constraints
to the task.

## Running & tooling

Use the Makefile; it exists so commands are discoverable and consistent.

```bash
make help        # list every target
make sync        # uv sync --all-extras --all-groups
make hooks       # pre-commit install, once per clone
make check       # lint + typecheck + test
make serve       # webapp with auto-reload (dev mode skips OAuth)
make docs        # mkdocs serve (make docs-build: strict, as CI)
```

**The pre-commit hooks run on every commit**, so write to pass them: ruff check and format,
pyright, stripped notebook outputs, no secrets, a single trailing newline. Never skip them with
`--no-verify`; fix the finding. `ruff` and `pyright` are pinned exactly and match the hook revs;
bump both together (`docs/guides/pre_commit.md`).

**Always run project code through `make`, or through `uv run --no-sync`.** A bare `uv run`
re-syncs the environment from `uv.lock` first, which silently reverts a local editable install of
lang-tools (`make dev-lang-tools`) or fastapi-tools (`make dev-fastapi-tools`). `make undev` is
the deliberate way back to the pinned tags. See `docs/guides/makefile.md`.

Credentials live in `~/cred/lang-tutor/.env` (template `nokeys.env`).

## Architecture

| Layer     | Path                          | Role                                                                |
| --------- | ----------------------------- | ------------------------------------------------------------------- |
| Content   | `src/lang_tutor/content/`     | the `http` / `in_process` content sources and their factory         |
| Exercises | `src/lang_tutor/exercises/`   | the five mechanics and the round / result protocol                  |
| Progress  | `src/lang_tutor/progress/`    | `UserLemmaProgress`, `compute_weight`, `select_lemmas`, `draw_cards` |
| LLM       | `src/lang_tutor/llm/`         | `build_tutor_chain`; prompt at `src/lang_tutor/prompts/tutor_response/` |
| Webapp    | `src/lang_tutor/webapp/`      | `build_app()`, pages, exercises API, auth, session state            |
| Params    | `src/lang_tutor/params/`, `config/` | `get_lang_tutor_params()`: paths, content, learner, llm, webapp |

- **Params** follow the config / params split in `docs/guides/params_config.md`. `LearnerParams`
  holds the target language and the known languages (`LANG_TUTOR_TARGET_LANGUAGE`,
  `LANG_TUTOR_KNOWN_LANGUAGES`), which every card read passes on.
- **Dev mode skips OAuth.** With `ENV_STAGE_TYPE=dev` the webapp injects a hardcoded dev user;
  webapp tests force prod mode with an autouse fixture to exercise the real auth path.
- **The tutor chain runs fake by default.** `LlmParams` supplies a `FakeChatModelConfig`, so no API
  key is needed until a real config is swapped in.

## Style rules

- Never use em dashes (`--`, `---`, or Unicode `—`). Use a hyphen `-` or rewrite the sentence.
- Use `loguru` (`from loguru import logger as lg`) for all logging.
- Raise descriptive named exceptions rather than bare `ValueError` / `RuntimeError`.
- Ruff runs with `select = ["ALL"]` and `target-version = "py314"`. Fix findings rather than adding
  `noqa`. Imports used only in annotations go under `if TYPE_CHECKING:`; the webapp is exempt
  because FastAPI reads route annotations at runtime, and a pydantic field type keeps its runtime
  import with `# noqa: TC00x` and the reason.

## Docstring style

**Google style** throughout, matching the rest of the fleet:

```python
def example(value: int) -> str:
    """One-line summary.

    Extended description as plain prose.

    Args:
        value: Description of the argument.

    Returns:
        Description of the return value.

    Raises:
        KeyError: If the key is missing.
    """
```

Never use NumPy / Sphinx RST underline headers (`Args\n----`). Section labels always take a
trailing colon. Module docstrings are narrative prose.

## Layout

- `tests/` mirrors `src/lang_tutor/`; it needs no lang-tools corpus.
- `static/` and `templates/` hold the webapp's assets and Jinja2 pages.
- `scratch_space/` is for throwaway prototyping notebooks. Planning for this repo lives in
  lang-tools' `scratch_space/` (see `CLAUDE.md`).
- `docs/` is the MkDocs site: `guides/` for tooling and procedures, `reference/` generated from
  docstrings (never write files there). Keep it current at the end of every task, updating
  statements in place rather than appending history.
