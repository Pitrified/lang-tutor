"""HTTP content source.

Reads content from the `lang-tools` HTTP read service. This is the default
transport in deployed setups: the operator runs `lang-tools` (cloned with
git-lfs so the content materialises) and `lang-tutor` consumes it over HTTP,
never storing content locally.

The content is public, so requests carry no authentication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from lang_tools.words.word import Word
from loguru import logger as lg

from lang_tutor.content.base import ContentSource

if TYPE_CHECKING:
    from collections.abc import Mapping

_WORDS_PATH = "/api/v1/words"
_DEFAULT_TIMEOUT = 10.0


class ContentServiceError(Exception):
    """Raised when the lang-tools content service returns an error response.

    Args:
        message: Human-readable description of the failure.
    """

    def __init__(self, message: str) -> None:
        """Initialize with a description of the failure.

        Args:
            message: Human-readable description of the failure.
        """
        super().__init__(message)


class HttpContentSource(ContentSource):
    """Content source backed by the `lang-tools` HTTP read service.

    Attributes:
        base_url: Base URL of the lang-tools service (no trailing slash).
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        client: httpx.Client | None = None,
    ) -> None:
        """Initialize the HTTP content source.

        Args:
            base_url: Base URL of the lang-tools service.
            timeout: Per-request timeout in seconds.
            client: Pre-built httpx client (mainly for tests). When None, a
                client bound to ``base_url`` is created.
        """
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(base_url=self.base_url, timeout=timeout)

    def get_words_filtered(
        self,
        language: str | None = None,
        topic: str | None = None,
    ) -> list[Word]:
        """Return words filtered by optional language and/or topic."""
        params: dict[str, str] = {}
        if language is not None:
            params["language"] = language
        if topic is not None:
            params["topic"] = topic
        payload = self._get_json(_WORDS_PATH, params=params)
        if not isinstance(payload, list):
            msg = f"Expected a list of words, got {type(payload).__name__}."
            raise ContentServiceError(msg)
        return [Word.model_validate(item) for item in payload]

    def get_word_by_id(self, word_id: str) -> Word | None:
        """Return a single word by its deterministic id, or None if absent."""
        try:
            response = self._client.get(f"{_WORDS_PATH}/{word_id}")
        except httpx.HTTPError as exc:
            msg = f"Failed to reach lang-tools service: {exc}"
            raise ContentServiceError(msg) from exc
        if response.status_code == httpx.codes.NOT_FOUND:
            return None
        self._raise_for_status(response)
        return Word.model_validate(response.json())

    def _get_json(self, path: str, *, params: Mapping[str, str]) -> object:
        """Issue a GET and return the decoded JSON body.

        Raises:
            ContentServiceError: When the request fails or returns a non-2xx
                status.
        """
        try:
            response = self._client.get(path, params=params)
        except httpx.HTTPError as exc:
            msg = f"Failed to reach lang-tools service: {exc}"
            raise ContentServiceError(msg) from exc
        self._raise_for_status(response)
        return response.json()

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Raise ContentServiceError for a non-2xx response."""
        if response.is_success:
            return
        lg.error(
            "lang-tools service error: {} {} -> {}",
            response.request.method,
            response.request.url,
            response.status_code,
        )
        msg = f"lang-tools service returned {response.status_code} for {response.url}."
        raise ContentServiceError(msg)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()
