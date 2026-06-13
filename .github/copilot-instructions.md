# lang-tutor - Copilot Instructions

## Project overview

`lang-tutor` is the **learner-facing tutoring + exercises app** of the language-learning ecosystem (Portuguese-focused but multi-language by design). It owns the stateful, per-user experience: the five exercise mechanics, per-user progress tracking and weighted word selection, the interactive tutor chain, and the FastAPI webapp (pages, runtime exercises API, Google OAuth, session state).

It depends on the companion **`lang-tools`** repo as a library for content: the `Word` model, the read/query helpers over the word store (`get_words_filtered`, `get_word_by_id`, ...), the `Language` presets, and the content-producing LLM chains. The dependency is strictly one-way - `lang-tutor` imports `lang-tools`, never the reverse. In phase 2 content is read **in-process** via the query helpers; phase 3 will switch content reads to an HTTP read API served by `lang-tools`. The split is tracked in `lang-tools`' `scratch_space/08_lang_tutor/`.

Python 3.14, managed with **uv**. Package name is `lang_tutor`.

## Running & tooling

```bash
uv run pytest                        # run tests
uv run ruff check .                  # lint (ruff, ALL rules enabled)
uv run pyright                       # type-check (src/ and tests/ only)

uv run mkdocs serve                  # MkDocs local docs server

# webapp dev server (dev mode bypasses OAuth with a hardcoded dev user)
uvicorn lang_tutor.webapp.app:app --reload
```

`lang-tools` is pinned in `pyproject.toml` as `lang-tools @ git+...@main` but overridden for local dev by an editable `[tool.uv.sources]` path to `../lang-tools`; the content (words CSVs in `lang-tools/data/`) is read from that checkout in-process.

Credentials live at `~/cred/lang-tutor/.env` (loaded by `load_env()` in `src/lang_tutor/params/load_env.py`).

## Architecture layers

| Layer        | Path                                               | Role                                                                     |
| ------------ | -------------------------------------------------- | ------------------------------------------------------------------------ |
| Params       | `src/lang_tutor/params/lang_tutor_params.py`       | Singleton `LangTutorParams`; aggregates paths, sample, llm, webapp params |
| Paths        | `src/lang_tutor/params/lang_tutor_paths.py`        | `LangTutorPaths`; env-aware filesystem references                        |
| Config       | `src/lang_tutor/config/`                           | Pydantic `BaseModelKwargs` models for typed settings (sample)            |
| Data models  | `src/lang_tutor/data_models/basemodel_kwargs.py`   | `BaseModelKwargs` - Pydantic base with `to_kw()` kwargs flattening       |
| Metaclasses  | `src/lang_tutor/metaclasses/singleton.py`          | `Singleton` metaclass                                                    |
| Env type     | `src/lang_tutor/params/env_type.py`                | `EnvStageType` (dev/prod) and `EnvLocationType` (local/render) enums     |

Domain layers (the tutoring concerns, all consuming `lang-tools` content):

| Layer        | Path                              | Role                                                                |
| ------------ | --------------------------------- | ------------------------------------------------------------------- |
| Exercises    | `src/lang_tutor/exercises/`       | The five mechanics (sentence reconstruction, pair matching, diacritic typing, wordle, conversational tutor) + round/result protocol |
| Progress     | `src/lang_tutor/progress/`        | `UserWordProgress`, `compute_weight`, weighted `select_words` over the `lang-tools` word pool |
| LLM (tutor)  | `src/lang_tutor/llm/`             | `build_tutor_chain` (interactive correction + conversation), prompt at `src/lang_tutor/prompts/tutor_response/` |
| Webapp       | `src/lang_tutor/webapp/`          | FastAPI `build_app()`, pages, runtime exercises API, OAuth/auth, services, session state |

## Key patterns

**`LangTutorParams` singleton**  
Access project-wide config via `get_lang_tutor_params()` from `src/lang_tutor/params/lang_tutor_params.py`. It aggregates `LangTutorPaths`, `SampleParams`, `LlmParams`, and `WebappParams`. Environment is controlled by `ENV_STAGE_TYPE` (`dev`/`prod`) and `ENV_LOCATION_TYPE` (`local`/`render`) env vars.

```python
from lang_tutor.params.lang_tutor_params import get_lang_tutor_params

params = get_lang_tutor_params()
paths = params.paths          # LangTutorPaths
llm = params.llm              # LlmParams (tutor chat config; fake mode by default)
webapp = params.webapp        # WebappParams
```

**`BaseModelKwargs`**  
Extend `BaseModelKwargs` (not plain `BaseModel`) for any config that needs to be forwarded as `**kwargs` to a third-party constructor. `to_kw(exclude_none=True)` flattens a nested `kwargs` dict at the top level.

```python
class SampleConfig(BaseModelKwargs):
    some_int: int
    nested_model: NestedModel
    kwargs: dict = Field(default_factory=dict)

cfg = SampleConfig(some_int=1, nested_model=NestedModel(some_str="hi"), kwargs={"extra": True})
cfg.to_kw(exclude_none=True)  # {"some_int": 1, "nested_model": ..., "extra": True}
```

**Config / Params separation**

- `src/lang_tutor/config/` holds Pydantic `BaseModelKwargs` models that define the _shape_ of settings. Use `SecretStr` for every sensitive field. Never read env vars inside config models.
- `src/lang_tutor/params/` holds plain classes that load _actual values_ and instantiate config models. Non-secret values are written as Python literals; env-switching is achieved via `match` on `env_type.stage` / `env_type.location`. Secrets are the only values loaded from `os.environ[VAR]` (raises `KeyError` naturally when missing).
- Every Params class accepts `env_type: EnvType | None = None` as its sole constructor argument. `__init__` only stores it and calls `_load_params()`. Loading is orchestrated via `_load_common_params()` then stage/location dispatch.
- Expose the assembled settings through `to_config()` returning the corresponding Pydantic model. Always mask secret fields in `__str__` using `[REDACTED]`.
- See `docs/guides/params_config.md` for the full reference with examples and common mistakes.

The canonical reference implementations are `src/lang_tutor/config/sample_config.py` and `src/lang_tutor/params/sample_params.py`.

**FastAPI webapp factory**  
`build_app()` in `src/lang_tutor/webapp/main.py` calls `fastapi-tools`' `create_app(config=...)` and registers the pages, exercises, words, progress, languages, and API v1 routers, with static files and Jinja2 templates. Entry point for uvicorn: `lang_tutor.webapp.app:app`.

Webapp config objects (`CORSConfig`, `SessionConfig`, `RateLimitConfig`, `GoogleOAuthConfig`) come from `fastapi-tools` and are assembled by `WebappParams` in `src/lang_tutor/params/webapp/webapp_params.py` (no local `config/webapp/`).

**OAuth dev bypass**  
`src/lang_tutor/webapp/core/auth.py` disables Google OAuth entirely in dev stage (`ENV_STAGE_TYPE=dev`) and injects a hardcoded dev user, so the app runs with zero config locally. `WebappParams` only requires `SESSION_SECRET_KEY` / `GOOGLE_CLIENT_ID` in prod. Webapp tests force prod mode via an autouse fixture to exercise the real auth path.

**Env-aware paths**  
`LangTutorPaths.load_config()` dispatches on `EnvLocationType` (`LOCAL` / `RENDER`) to set environment-specific paths. Common paths (`root_fol`, `cache_fol`, `data_fol`, `static_fol`, `templates_fol`) are always set in `load_common_config_pre()`.

**`Singleton` metaclass**  
Use `metaclass=Singleton` for any class that must have exactly one instance per process (e.g., `LangTutorParams`). Reset in tests by clearing `Singleton._instances`.

**Tutor LLM chain**  
`build_tutor_chain(chat_config)` in `src/lang_tutor/llm/tutor.py` builds an `llm-core` `StructuredLLMChain[TutorInput, TutorOutput]` from the versioned prompt at `src/lang_tutor/prompts/tutor_response/vN.jinja` (loaded via the in-package `llm/_common.py`). `LlmParams` supplies the chat config (a `FakeChatModelConfig` by default - no API key needed; swap to a real config when ready).

## Style rules

- Never use em dashes (`--` or `---` or Unicode `—`). Use a hyphen `-` or rewrite the sentence.
- Use `loguru` (`from loguru import logger as lg`) for all logging.
- Raise descriptive custom exceptions (e.g., `UnknownEnvLocationError`) rather than bare `ValueError`/`RuntimeError`.

## Documentation

Always keep the `docs/` folder updated at the end of a task.

### Docs folder

- `docs/` holds MkDocs source. `mkdocs.yml` configures the site with the Material theme, mkdocstrings for API reference.
- `docs/guides/` holds narrative guides related to tooling, setup, and project conventions. These are not part of the API reference and should not be written in docstring style.
- `docs/library/` holds description of the core library code. This is not an API reference; write in narrative style with custom headings as needed. Can create subfolders for different domains.
- `docs/reference/` is a virtual folder generated by `mkdocstrings` from docstrings in the source code. Do not write any files here; write docstrings in the source code instead. To reference a file inside this section, link using this structure: [`<some class/function name>`](,,/../reference/lang_tutor/config/sample_config/) which would link to `src/lang_tutor/config/sample_config.py`'s API reference page.

### Docstring style

Use **Google style** throughout. mkdocstrings is configured with `docstring_style: "google"`.

Standard sections use a label followed by a colon, with content indented by 4 spaces:

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

    Example:
        Brief usage example::

            result = example(42)
    """
```

**Never use NumPy / Sphinx RST underline-style headers** (`Args\n----`, `Returns\n-------`, `Attributes\n----------`, etc.).

Rules:
- Section labels: `Args:`, `Returns:`, `Raises:`, `Attributes:`, `Note:`, `Warning:`, `See Also:`, `Example:`, `Examples:` - always with a trailing colon, never with an underline.
- `Attributes:` in class docstrings uses two levels of indentation: the attribute name at +4 spaces, its description at +8 spaces.
- Module docstrings are narrative prose. Custom topic headings (e.g., "Pattern rules") are written as plain labelled paragraphs (`Pattern rules:`) - no underline, no RST heading markup.
- `See Also:` lists items as bare lines indented under the section label, not as `*` bullets.

## Testing & scratch space

- Tests live in `tests/` mirroring `src/lang_tutor/` structure.
- `scratch_space/` holds numbered exploratory notebooks and scripts. Not part of the package; ruff ignores `ERA001`/`F401`/`T20` there.

## Linting notes

- `ruff.toml` targets Python 3.13 with `select = ["ALL"]`. Key ignores: `COM812`, `D104`, `D203`, `D213`, `D413`, `FIX002`, `RET504`, `TD002`, `TD003`.
- Tests additionally allow `ARG001`, `D103`, `INP001`, `PLR2004`, `S101`, `S311`.
- `src/lang_tutor/webapp/**` additionally allows `ARG001` (FastAPI DI) and `S311` (game randomness, not crypto).
- Notebooks (`*.ipynb`) additionally allow `E501`, `ERA001`, `F401`, `S311`, `T20`.
- `meta/*` additionally allows `INP001`, `T20`.
- `max-args = 10` (pylint).

## End-of-task verification

After every code change, run the full verification suite before considering the task done:

```bash
uv run pytest && uv run ruff check . && uv run pyright
```

Then update the docs.
