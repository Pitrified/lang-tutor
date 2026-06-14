# Content source (where words come from)

`lang-tutor` reads word content through a single seam, `ContentSource`, with two
interchangeable implementations. The transport is chosen by configuration, so
the rest of the app (exercises, word browsing) never knows whether content
arrives over HTTP or from an in-process read.

```python
from lang_tutor.content import get_content_source

words = get_content_source().get_words_filtered(language="pt")
word = get_content_source().get_word_by_id(word_id)
```

## The two sources

| Source | Class | When to use |
| ------ | ----- | ----------- |
| HTTP (default) | `HttpContentSource` | Deployed topology: `lang-tools` runs as a service and `lang-tutor` consumes it over HTTP, never storing content locally. |
| In-process | `InProcessContentSource` | Local/dev without running the service. Reads the `lang-tools` word store directly (requires the content materialised on disk via git-lfs). |

Both return the same `lang_tools.words.word.Word` model - including the computed
fields (`id`, `has_accent`, `length`, ...) the exercises rely on - so they are
drop-in interchangeable.

## Configuration

Selection lives in `ContentParams`, driven by environment variables:

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `LANG_TOOLS_CONTENT_SOURCE` | `http` | `http` or `in_process`. |
| `LANG_TOOLS_BASE_URL` | `http://localhost:8010` | Base URL of the `lang-tools` service (used when source is `http`). |

```bash
# Default: consume the running lang-tools service
export LANG_TOOLS_CONTENT_SOURCE=http
export LANG_TOOLS_BASE_URL=http://127.0.0.1:8010

# Dev without the service: read the lang-tools store in-process
export LANG_TOOLS_CONTENT_SOURCE=in_process
```

To run the HTTP path locally, start the `lang-tools` read service first (see the
`lang-tools` "Running the read service" guide), then point
`LANG_TOOLS_BASE_URL` at it.

## Error handling

`HttpContentSource` maps a `404` on `get_word_by_id` to `None` (consistent with
the in-process store). Any other non-2xx response, or a transport failure,
raises `ContentServiceError`.

## Overriding in tests

`set_content_source()` swaps the process-wide source (or pass `None` to clear
the cache so the next call rebuilds from params):

```python
from lang_tutor.content import factory
from lang_tutor.content.in_process import InProcessContentSource

factory.set_content_source(InProcessContentSource())
```
