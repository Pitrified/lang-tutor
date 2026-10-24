"""Tests for the HTTP content source using a mocked transport."""

import httpx
from lang_tools.lexicon import CardQuery
from lang_tools.lexicon import Lemma
from lang_tools.lexicon import LemmaCard
import pytest

from lang_tutor.content.http import ContentServiceError
from lang_tutor.content.http import HttpContentSource

_BASE_URL = "http://lang-tools.test"

_CASA = Lemma(text="casa", language="pt")
_AGUA = Lemma(text="água", language="pt", topics=["food"])
_LEMMAS = [_CASA, _AGUA]
_BY_ID = {lemma.id: lemma for lemma in _LEMMAS}
_CARDS = {
    lemma.id: LemmaCard(lemma=lemma, cefr_level="A1", translations={"en": ["x"]})
    for lemma in _LEMMAS
}

#: Every request the mock saw, for asserting on the encoded query string.
_SEEN: list[httpx.Request] = []


def _handler(request: httpx.Request) -> httpx.Response:
    """Mimic the lang-tools lemma and card read API."""
    _SEEN.append(request)
    path = request.url.path
    params = request.url.params
    if path == "/api/v1/lemmas":
        lemmas = _LEMMAS
        if params.get("language"):
            lemmas = [lem for lem in lemmas if lem.language == params["language"]]
        if params.get("topic"):
            lemmas = [lem for lem in lemmas if params["topic"] in lem.topics]
        total = len(lemmas)
        offset = int(params.get("offset", 0))
        lemmas = lemmas[offset : offset + int(params.get("limit", 100))]
        return httpx.Response(
            200,
            json=[lemma.model_dump(mode="json") for lemma in lemmas],
            headers={"X-Total-Count": str(total)},
        )
    if path == "/api/v1/cards":
        limit = int(params.get("limit", 50))
        cards = list(_CARDS.values())[:limit]
        return httpx.Response(
            200, json=[card.model_dump(mode="json") for card in cards]
        )
    if path.startswith("/api/v1/cards/") and path.endswith("/senses"):
        card = _CARDS.get(path.removeprefix("/api/v1/cards/").removesuffix("/senses"))
        cards = [card] if card else []
        return httpx.Response(200, json=[c.model_dump(mode="json") for c in cards])
    for prefix, table in (("/api/v1/lemmas/", _BY_ID), ("/api/v1/cards/", _CARDS)):
        if path.startswith(prefix):
            item = table.get(path.removeprefix(prefix))
            if item is None:
                return httpx.Response(404, json={"detail": "not found"})
            return httpx.Response(200, json=item.model_dump(mode="json"))
    return httpx.Response(404)


def _make_source() -> HttpContentSource:
    """Build an HTTP content source wired to the mock transport."""
    _SEEN.clear()
    client = httpx.Client(
        base_url=_BASE_URL,
        transport=httpx.MockTransport(_handler),
    )
    return HttpContentSource(base_url=_BASE_URL, client=client)


def test_get_cards_parses_cards() -> None:
    """The JSON list is parsed into LemmaCard models."""
    source = _make_source()
    cards = source.get_cards(CardQuery(language="pt", limit=1))
    assert len(cards) == 1
    assert isinstance(cards[0], LemmaCard)
    assert cards[0].lemma.text == "casa"


def test_card_query_is_encoded_with_repeated_keys() -> None:
    """Only non-default fields are sent; lists repeat the key; bools lowercase."""
    source = _make_source()
    source.get_cards(
        CardQuery(
            language="pt",
            single_word=True,
            max_cefr="B1",
            translation_languages=["en", "it"],
        ),
    )
    sent = _SEEN[-1].url.params
    assert sent.get_list("translation_languages") == ["en", "it"]
    assert sent["single_word"] == "true"
    assert sent["max_cefr"] == "B1"
    assert "order" not in sent  # a default is left to the service


def test_get_card_found_and_missing() -> None:
    """A known id resolves to its card; a 404 maps to None."""
    source = _make_source()
    card = source.get_card(
        _CASA.id,
        translation_languages=["en", "it"],
        known_languages=["en", "it"],
    )
    assert card is not None
    assert card.lemma.text == "casa"
    assert _SEEN[-1].url.params.get_list("translation_languages") == ["en", "it"]
    assert _SEEN[-1].url.params.get_list("known_languages") == ["en", "it"]
    assert source.get_card("nope") is None


def test_get_sense_cards() -> None:
    """The per-sense list parses; an unknown lemma has none."""
    source = _make_source()
    cards = source.get_sense_cards(_CASA.id, gloss_language="pt")
    assert [card.lemma.text for card in cards] == ["casa"]
    assert _SEEN[-1].url.params["gloss_language"] == "pt"
    assert source.get_sense_cards("nope") == []


def test_get_lemma_page_reads_the_total_header() -> None:
    """The page is parsed and its total comes from X-Total-Count."""
    source = _make_source()
    page = source.get_lemma_page(language="pt", limit=1)
    assert [lemma.text for lemma in page.lemmas] == ["casa"]
    assert page.total == 2
    by_topic = source.get_lemma_page(topic="food")
    assert [lemma.text for lemma in by_topic.lemmas] == ["água"]


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
        source.get_cards(CardQuery())
    with pytest.raises(ContentServiceError):
        source.get_card("anything")


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
