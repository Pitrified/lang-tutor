"""Content source factory.

Builds the `ContentSource` selected by `ContentParams` and caches it for the
process. Call sites use `get_content_source()`; the chosen transport (HTTP by
default, in-process for local/dev) is decided here, in one place.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger as lg

from lang_tutor.content.http import HttpContentSource
from lang_tutor.content.in_process import InProcessContentSource
from lang_tutor.params.content_params import UnknownContentSourceError
from lang_tutor.params.lang_tutor_params import get_content_params

if TYPE_CHECKING:
    from lang_tutor.content.base import ContentSource

_content_source: ContentSource | None = None


def _build_content_source() -> ContentSource:
    """Build the content source selected by the content params."""
    params = get_content_params()
    match params.source:
        case "in_process":
            lg.info("Using in-process content source")
            return InProcessContentSource()
        case "http":
            lg.info("Using HTTP content source: {}", params.base_url)
            return HttpContentSource(base_url=params.base_url)
        case _:  # pragma: no cover - guarded by ContentParams validation
            raise UnknownContentSourceError(params.source)


def get_content_source() -> ContentSource:
    """Return the process-wide content source, building it on first use.

    Returns:
        The configured `ContentSource` (HTTP by default, in-process for dev).
    """
    global _content_source  # noqa: PLW0603
    if _content_source is None:
        _content_source = _build_content_source()
    return _content_source


def set_content_source(source: ContentSource | None) -> None:
    """Override the cached content source (mainly for tests).

    Args:
        source: The content source to use, or None to clear the cache so the
            next `get_content_source()` rebuilds from params.
    """
    global _content_source  # noqa: PLW0603
    _content_source = source
