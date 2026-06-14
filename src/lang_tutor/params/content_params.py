"""Content source params for lang-tutor.

Selects where word/sentence content comes from: the `lang-tools` HTTP read
service (the default, matching the deployed topology) or an in-process read of
the `lang-tools` word store (handy for local/dev without running the service).

Environment variables:
    LANG_TOOLS_CONTENT_SOURCE: ``http`` (default) or ``in_process``.
    LANG_TOOLS_BASE_URL: base URL of the lang-tools service when source=http.
        Defaults to ``http://localhost:8010``.
"""

from __future__ import annotations

import os
from typing import Literal
from typing import get_args

from loguru import logger as lg

ContentSourceKind = Literal["http", "in_process"]

_DEFAULT_BASE_URL = "http://localhost:8010"


class UnknownContentSourceError(Exception):
    """Raised when LANG_TOOLS_CONTENT_SOURCE holds an unsupported value.

    Args:
        value: The unrecognised content source value.
    """

    def __init__(self, value: str) -> None:
        """Initialize with the invalid value.

        Args:
            value: The unrecognised content source value.
        """
        self.value = value
        allowed = ", ".join(get_args(ContentSourceKind))
        message = f"Unknown content source: {value!r}. Expected one of: {allowed}."
        super().__init__(message)


class ContentParams:
    """Content source parameters loaded from environment variables."""

    def __init__(self) -> None:
        """Load content params from environment."""
        lg.info("Loading ContentParams")
        self._load_params()

    def _load_params(self) -> None:
        """Read the content source selection and base URL from the environment."""
        source = os.getenv("LANG_TOOLS_CONTENT_SOURCE", "http").lower()
        if source not in get_args(ContentSourceKind):
            raise UnknownContentSourceError(source)
        self.source: ContentSourceKind = source  # type: ignore[assignment]

        base_url = os.getenv("LANG_TOOLS_BASE_URL", _DEFAULT_BASE_URL)
        self.base_url: str = base_url.rstrip("/")

    def __str__(self) -> str:
        """Return the string representation of the object."""
        s = "ContentParams:"
        s += f"\n  source: {self.source}"
        s += f"\n  base_url: {self.base_url}"
        return s
