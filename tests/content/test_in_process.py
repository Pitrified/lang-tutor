"""Tests for the in-process content source, over a small fixture store."""

from collections.abc import Generator

from lang_tools.lexicon import CardQuery
from lang_tools.lexicon import Concept
from lang_tools.lexicon import Lemma
from lang_tools.lexicon import LexiconStore
from lang_tools.lexicon import Sense
from lang_tools.lexicon.lemma_store import reset_store
from lang_tools.lexicon.lemma_store import set_store
import pytest

from lang_tutor.content.in_process import InProcessContentSource

C_HOUSE = "c__house-building__0011aabbccdd"

_CASA = Lemma(text="casa", language="pt")
_CAFE = Lemma(text="café", language="pt")
_HOUSE = Lemma(text="house", language="en")


@pytest.fixture(autouse=True)
def _fixture_store() -> Generator[None]:
    """Point the process-wide lexicon store at a three-lemma graph."""
    set_store(
        LexiconStore.from_models(
            lemmas=[_CASA, _CAFE, _HOUSE],
            concepts=[Concept(id=C_HOUSE, definitions={"en": "a building"})],
            senses=[
                Sense(lemma_id=_CASA.id, concept_id=C_HOUSE, cefr_level="A1"),
                Sense(lemma_id=_HOUSE.id, concept_id=C_HOUSE, cefr_level="A1"),
            ],
            false_friends=[],
            concept_relations=[],
            sense_relations=[],
        ),
    )
    yield
    reset_store()


def test_get_cards_reads_the_store() -> None:
    """Cards come back with the best sense's gloss and translations."""
    source = InProcessContentSource()
    cards = source.get_cards(CardQuery(language="pt", require_translation=True))
    assert [card.lemma.text for card in cards] == ["casa"]
    assert cards[0].translations == {"en": ["house"]}
    assert cards[0].gloss == "a building"


def test_get_card_found_and_missing() -> None:
    """One lemma's card, or None for an unknown id."""
    source = InProcessContentSource()
    card = source.get_card(_CASA.id)
    assert card is not None
    assert card.cefr_level == "A1"
    assert source.get_card("does-not-exist") is None


def test_get_lemma_page_pages_and_counts() -> None:
    """A page is bounded and carries the total match count."""
    source = InProcessContentSource()
    page = source.get_lemma_page(language="pt", limit=1)
    assert [lemma.text for lemma in page.lemmas] == ["café"]
    assert page.total == 2
    searched = source.get_lemma_page(query="CAS")
    assert [lemma.text for lemma in searched.lemmas] == ["casa"]


def test_get_lemma_by_id_round_trip() -> None:
    """A lemma resolves by its id; an unknown id resolves to None."""
    source = InProcessContentSource()
    fetched = source.get_lemma_by_id(_CASA.id)
    assert fetched is not None
    assert fetched.text == "casa"
    assert source.get_lemma_by_id("does-not-exist") is None
