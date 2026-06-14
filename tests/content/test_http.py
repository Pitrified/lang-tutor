"""Tests for the HTTP content source using a mocked transport."""

import httpx
from lang_tools.words.word import Word
import pytest

from lang_tutor.content.http import ContentServiceError
from lang_tutor.content.http import HttpContentSource

_BASE_URL = "http://lang-tools.test"

_CASA = Word(text="casa", language="pt", translations={"en": "house"})
_AGUA = Word(text="água", language="pt", topics=["food"])
_WORDS = [_CASA, _AGUA]
_BY_ID = {w.id: w for w in _WORDS}


def _handler(request: httpx.Request) -> httpx.Response:
    """Mimic the lang-tools word read API."""
    path = request.url.path
    if path == "/api/v1/words":
        language = request.url.params.get("language")
        topic = request.url.params.get("topic")
        words = _WORDS
        if language:
            words = [w for w in words if w.language == language]
        if topic:
            words = [w for w in words if topic in w.topics]
        return httpx.Response(200, json=[w.model_dump(mode="json") for w in words])
    prefix = "/api/v1/words/"
    if path.startswith(prefix):
        word_id = path.removeprefix(prefix)
        word = _BY_ID.get(word_id)
        if word is None:
            return httpx.Response(404, json={"detail": f"Word not found: {word_id}"})
        return httpx.Response(200, json=word.model_dump(mode="json"))
    return httpx.Response(404)


def _make_source() -> HttpContentSource:
    """Build an HTTP content source wired to the mock transport."""
    client = httpx.Client(
        base_url=_BASE_URL,
        transport=httpx.MockTransport(_handler),
    )
    return HttpContentSource(base_url=_BASE_URL, client=client)


def test_get_words_filtered_parses_words() -> None:
    """The source parses the JSON list into Word models."""
    source = _make_source()
    words = source.get_words_filtered()
    assert {w.text for w in words} == {"casa", "água"}
    assert all(isinstance(w, Word) for w in words)


def test_get_words_filtered_passes_filters() -> None:
    """Language and topic filters are forwarded as query params."""
    source = _make_source()
    by_topic = source.get_words_filtered(topic="food")
    assert [w.text for w in by_topic] == ["água"]


def test_get_word_by_id_found() -> None:
    """A known id resolves to its word."""
    source = _make_source()
    fetched = source.get_word_by_id(_CASA.id)
    assert fetched is not None
    assert fetched.text == "casa"


def test_get_word_by_id_missing_returns_none() -> None:
    """A 404 from the service maps to None, not an error."""
    source = _make_source()
    assert source.get_word_by_id("nope") is None


def test_server_error_raises() -> None:
    """A non-2xx (other than 404) response raises ContentServiceError."""

    def _failing(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "boom"})

    client = httpx.Client(
        base_url=_BASE_URL,
        transport=httpx.MockTransport(_failing),
    )
    source = HttpContentSource(base_url=_BASE_URL, client=client)
    with pytest.raises(ContentServiceError):
        source.get_words_filtered()


def test_connection_error_raises() -> None:
    """A transport-level failure is wrapped in ContentServiceError."""

    def _boom(_request: httpx.Request) -> httpx.Response:
        msg = "no route to host"
        raise httpx.ConnectError(msg)

    client = httpx.Client(
        base_url=_BASE_URL,
        transport=httpx.MockTransport(_boom),
    )
    source = HttpContentSource(base_url=_BASE_URL, client=client)
    with pytest.raises(ContentServiceError):
        source.get_word_by_id("anything")
