"""HTTP content source.

Reads content from the `lang-tools` HTTP read service. This is the default
transport in deployed setups: the operator runs `lang-tools` (cloned with
git-lfs so the content materialises) and `lang-tutor` consumes it over HTTP,
never storing content locally.

The content is public, so requests carry no authentication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Literal
from typing import overload

import httpx
from lang_tools.lexicon import Lemma
from lang_tools.lexicon import LemmaCard
from loguru import logger as lg

from lang_tutor.content.base import ContentSource
from lang_tutor.content.base import LemmaPage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from lang_tools.lexicon import CardQuery

#: Query parameters as httpx takes them; a list of pairs repeats a key, which is
#: how the service reads list fields (``translation_languages=en&...=it``).
type QueryParams = list[tuple[str, str]]

_LEMMAS_PATH = "/api/v1/lemmas"
_CARDS_PATH = "/api/v1/cards"
_TOTAL_HEADER = "X-Total-Count"
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

    def get_cards(self, query: CardQuery) -> list[LemmaCard]:
        """Return up to ``query.limit`` drill cards matching the filters."""
        payload = self._get(_CARDS_PATH, params=_card_params(query)).json()
        if not isinstance(payload, list):
            msg = f"Expected a list of cards, got {type(payload).__name__}."
            raise ContentServiceError(msg)
        return [LemmaCard.model_validate(item) for item in payload]

    def get_card(
        self,
        lemma_id: str,
        *,
        gloss_language: str = "en",
        translation_languages: Sequence[str] = ("en",),
        known_languages: Sequence[str] = (),
    ) -> LemmaCard | None:
        """Return the drill card of one lemma, or None if absent."""
        params = _card_lookup_params(
            gloss_language,
            translation_languages,
            known_languages,
        )
        path = f"{_CARDS_PATH}/{lemma_id}"
        response = self._get(path, params=params, missing_ok=True)
        if response is None:
            return None
        return LemmaCard.model_validate(response.json())

    def get_sense_cards(
        self,
        lemma_id: str,
        *,
        gloss_language: str = "en",
        translation_languages: Sequence[str] = ("en",),
        known_languages: Sequence[str] = (),
    ) -> list[LemmaCard]:
        """Return one card per sense of a lemma, best sense first."""
        params = _card_lookup_params(
            gloss_language,
            translation_languages,
            known_languages,
        )
        payload = self._get(f"{_CARDS_PATH}/{lemma_id}/senses", params=params).json()
        if not isinstance(payload, list):
            msg = f"Expected a list of cards, got {type(payload).__name__}."
            raise ContentServiceError(msg)
        return [LemmaCard.model_validate(item) for item in payload]

    def get_lemma_page(
        self,
        *,
        language: str | None = None,
        topic: str | None = None,
        query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> LemmaPage:
        """Return one page of lemmas and the total match count."""
        params: QueryParams = [("limit", str(limit)), ("offset", str(offset))]
        for key, value in (("language", language), ("topic", topic), ("q", query)):
            if value is not None:
                params.append((key, value))
        response = self._get(_LEMMAS_PATH, params=params)
        payload = response.json()
        if not isinstance(payload, list):
            msg = f"Expected a list of lemmas, got {type(payload).__name__}."
            raise ContentServiceError(msg)
        lemmas = [Lemma.model_validate(item) for item in payload]
        total = int(response.headers.get(_TOTAL_HEADER, len(lemmas)))
        return LemmaPage(lemmas=lemmas, total=total)

    def get_lemma_by_id(self, lemma_id: str) -> Lemma | None:
        """Return a single lemma by its deterministic id, or None if absent."""
        response = self._get(f"{_LEMMAS_PATH}/{lemma_id}", missing_ok=True)
        if response is None:
            return None
        return Lemma.model_validate(response.json())

    @overload
    def _get(
        self,
        path: str,
        *,
        params: QueryParams | None = None,
        missing_ok: Literal[False] = False,
    ) -> httpx.Response: ...

    @overload
    def _get(
        self,
        path: str,
        *,
        params: QueryParams | None = None,
        missing_ok: Literal[True],
    ) -> httpx.Response | None: ...

    def _get(
        self,
        path: str,
        *,
        params: QueryParams | None = None,
        missing_ok: bool = False,
    ) -> httpx.Response | None:
        """Issue a GET and return the successful response.

        Args:
            path: Path under the service base URL.
            params: Query parameters (a list of pairs, so keys can repeat).
            missing_ok: Return None on a 404 instead of raising.

        Returns:
            The 2xx response, or None for a 404 when ``missing_ok``.

        Raises:
            ContentServiceError: When the request fails or returns a non-2xx
                status (other than an allowed 404).
        """
        try:
            # A tuple, not the list: httpx's params type is a covariant sequence.
            response = self._client.get(path, params=tuple(params or ()))
        except httpx.HTTPError as exc:
            msg = f"Failed to reach lang-tools service: {exc}"
            raise ContentServiceError(msg) from exc
        if missing_ok and response.status_code == httpx.codes.NOT_FOUND:
            return None
        self._raise_for_status(response)
        return response

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


def _card_lookup_params(
    gloss_language: str,
    translation_languages: Sequence[str],
    known_languages: Sequence[str] = (),
) -> QueryParams:
    """Encode the languages of a per-lemma card read."""
    params: QueryParams = [("gloss_language", gloss_language)]
    params += [("translation_languages", lang) for lang in translation_languages]
    params += [("known_languages", lang) for lang in known_languages]
    return params


def _card_params(query: CardQuery) -> QueryParams:
    """Encode a `CardQuery` as repeated-key query parameters.

    Only fields that differ from their defaults are sent, so the service applies
    its own defaults; list fields become one pair per item, booleans the
    lowercase ``true`` / ``false`` FastAPI parses.
    """
    params: QueryParams = []
    for key, value in query.model_dump(exclude_defaults=True).items():
        items = value if isinstance(value, list) else [value]
        for item in items:
            text = str(item).lower() if isinstance(item, bool) else str(item)
            params.append((key, text))
    return params
