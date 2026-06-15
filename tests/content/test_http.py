"""Tests for the HTTP content source using a mocked transport."""

import httpx
from lang_tools.lexicon.lemma import Lemma
import pytest

from lang_tutor.content.http import ContentServiceError
from lang_tutor.content.http import HttpContentSource

_BASE_URL = "http://lang-tools.test"

_CASA = Lemma(text="casa", language="pt", translations={"en": "house"})
_AGUA = Lemma(text="água", language="pt", topics=["food"])
_LEMMAS = [_CASA, _AGUA]
_BY_ID = {lemma.id: lemma for lemma in _LEMMAS}


def _handler(request: httpx.Request) -> httpx.Response:
    """Mimic the lang-tools lemma read API."""
    path = request.url.path
    if path == "/api/v1/lemmas":
        language = request.url.params.get("language")
        topic = request.url.params.get("topic")
        lemmas = _LEMMAS
        if language:
            lemmas = [lemma for lemma in lemmas if lemma.language == language]
        if topic:
            lemmas = [lemma for lemma in lemmas if topic in lemma.topics]
        return httpx.Response(
            200,
            json=[lemma.model_dump(mode="json") for lemma in lemmas],
        )
    prefix = "/api/v1/lemmas/"
    if path.startswith(prefix):
        lemma_id = path.removeprefix(prefix)
        lemma = _BY_ID.get(lemma_id)
        if lemma is None:
            return httpx.Response(404, json={"detail": f"Lemma not found: {lemma_id}"})
        return httpx.Response(200, json=lemma.model_dump(mode="json"))
    return httpx.Response(404)


def _make_source() -> HttpContentSource:
    """Build an HTTP content source wired to the mock transport."""
    client = httpx.Client(
        base_url=_BASE_URL,
        transport=httpx.MockTransport(_handler),
    )
    return HttpContentSource(base_url=_BASE_URL, client=client)


def test_get_lemmas_filtered_parses_lemmas() -> None:
    """The source parses the JSON list into Lemma models."""
    source = _make_source()
    lemmas = source.get_lemmas_filtered()
    assert {lemma.text for lemma in lemmas} == {"casa", "água"}
    assert all(isinstance(lemma, Lemma) for lemma in lemmas)


def test_get_lemmas_filtered_passes_filters() -> None:
    """Language and topic filters are forwarded as query params."""
    source = _make_source()
    by_topic = source.get_lemmas_filtered(topic="food")
    assert [lemma.text for lemma in by_topic] == ["água"]


def test_get_lemma_by_id_found() -> None:
    """A known id resolves to its lemma."""
    source = _make_source()
    fetched = source.get_lemma_by_id(_CASA.id)
    assert fetched is not None
    assert fetched.text == "casa"


def test_get_lemma_by_id_missing_returns_none() -> None:
    """A 404 from the service maps to None, not an error."""
    source = _make_source()
    assert source.get_lemma_by_id("nope") is None


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
        source.get_lemmas_filtered()


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
        source.get_lemma_by_id("anything")
