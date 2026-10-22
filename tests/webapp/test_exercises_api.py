"""Tests for the exercise JSON API over a small fixture lexicon."""

from collections.abc import Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_tools import create_app
from fastapi_tools.config.webapp_config import WebappConfig
from fastapi_tools.schemas.auth import SessionData
from lang_tools.lexicon import Concept
from lang_tools.lexicon import Lemma
from lang_tools.lexicon import LexiconStore
from lang_tools.lexicon import Sense
from lang_tools.lexicon.lemma_store import reset_store
from lang_tools.lexicon.lemma_store import set_store
import pytest

from lang_tutor.content import InProcessContentSource
from lang_tutor.content import set_content_source
from lang_tutor.exercises.sentence_reconstruction import merge_short_portions
from lang_tutor.webapp.api.v1.api_router import router as api_router
from lang_tutor.webapp.routers.lemmas_router import router as lemmas_router
from lang_tutor.webapp.services.progress_service import get_progress_service

from .conftest import _STATIC_DIR
from .conftest import _TEMPLATES_DIR

#: (pt, en, gloss, cefr) for each fixture concept.
_WORDS = (
    ("casa", "house", "a building to live in", "A1"),
    ("livro", "book", "a written work", "A1"),
    ("água", "water", "a clear liquid", "A1"),
    ("porta", "door", "a movable barrier", "A2"),
    ("café", "coffee", "a hot drink", "A1"),
    ("Lisboa", "Lisbon", "capital of Portugal", "B1"),
)
_SENTENCE: str = "A casa é grande."

LEMMA_IDS = {pt: Lemma(text=pt, language="pt").id for pt, *_ in _WORDS}


def _store() -> LexiconStore:
    lemmas: list[Lemma] = []
    concepts: list[Concept] = []
    senses: list[Sense] = []
    for index, (pt, en, gloss, level) in enumerate(_WORDS):
        cid = f"c__{en.lower()}__{index:012x}"
        examples = {"pt": [_SENTENCE]} if pt == "casa" else {}
        concepts.append(Concept(id=cid, definitions={"en": gloss}, examples=examples))
        for text, language in ((pt, "pt"), (en, "en")):
            lemma = Lemma(text=text, language=language, part_of_speech="noun")
            lemmas.append(lemma)
            senses.append(
                Sense(
                    lemma_id=lemma.id,
                    concept_id=cid,
                    cefr_level=level,
                    sense_frequency=4.0,
                ),
            )
    return LexiconStore.from_models(
        lemmas=lemmas,
        concepts=concepts,
        senses=senses,
        false_friends=[],
        concept_relations=[],
        sense_relations=[],
    )


@pytest.fixture(autouse=True)
def _fixture_content() -> Generator[None]:
    """Serve the fixture lexicon through the in-process content source."""
    set_store(_store())
    set_content_source(InProcessContentSource())
    yield
    set_content_source(None)
    reset_store()


@pytest.fixture
def app(test_config: WebappConfig) -> FastAPI:
    """Build the app with the exercise API and the lemma pages."""
    return create_app(
        config=test_config,
        extra_routers=[api_router, lemmas_router],
        static_dir=_STATIC_DIR,
        templates_dir=_TEMPLATES_DIR,
    )


def _post(client: TestClient, path: str, body: dict | None = None) -> dict:
    response = client.post(f"/api/v1/exercises/{path}", json=body or {})
    assert response.status_code == 200, response.text
    return response.json()["data"]


def test_pair_matching_round_and_progress(
    authenticated_client: TestClient,
    mock_session_data: SessionData,
) -> None:
    """A round pairs single words only, and a tap is recorded as progress."""
    data = _post(authenticated_client, "pair-matching/start", {"num_lemmas": 3})
    assert len(data["left_lemmas"]) == 3
    assert "Lisboa" not in data["left_lemmas"]  # a proper noun is no drill word
    english = {pt: en for pt, en, *_ in _WORDS}
    left = data["left_lemmas"][0]
    result = _post(
        authenticated_client,
        "pair-matching/submit",
        {"left": left, "right": english[left]},
    )
    assert result["correct"] is True
    progress = get_progress_service().for_user(mock_session_data.user_id)
    record = progress[LEMMA_IDS[left]]
    assert record.correct_count == 1
    assert record.exercise_stats["pair_matching"].seen_count == 1


def test_pair_matching_rejects_an_unknown_language(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.post(
        "/api/v1/exercises/pair-matching/start",
        json={"language": "xx"},
    )
    assert response.status_code == 400


def test_wordle_targets_a_level_appropriate_word(
    authenticated_client: TestClient,
) -> None:
    data = _post(authenticated_client, "wordle/start", {"word_length": 5})
    assert data["word_length"] == 5
    guess = _post(authenticated_client, "wordle/guess", {"guess": "zzzzz"})
    assert guess["correct"] is False
    # Only livro and porta are 5-letter single words; B1 Lisboa is 6 and capital.
    too_hard = authenticated_client.post(
        "/api/v1/exercises/wordle/start",
        json={"word_length": 6},
    )
    assert too_hard.status_code == 400


def test_diacritic_typing_shows_meaning_hints(
    authenticated_client: TestClient,
) -> None:
    data = _post(authenticated_client, "diacritic-typing/start")
    assert data["translation"] in {"water", "coffee"}
    assert data["glosses"] in (["a clear liquid"], ["a hot drink"])
    assert data["word_length"] == len(data["display"])


def test_sentence_reconstruction_round(
    authenticated_client: TestClient,
    mock_session_data: SessionData,
) -> None:
    """The prompt names the drilled lemma; one submit finishes the round."""
    data = _post(authenticated_client, "sentence-reconstruction/start")
    assert "casa" in data["translation"]
    assert "house" in data["translation"]
    words: list[str] = _SENTENCE.split()
    ordered = merge_short_portions(words)
    assert sorted(data["portions"]) == sorted(ordered)
    result = _post(
        authenticated_client,
        "sentence-reconstruction/submit",
        {"selected_portions": ordered},
    )
    assert result == {"correct": True, "finished": True, "answer": _SENTENCE}
    progress = get_progress_service().for_user(mock_session_data.user_id)
    assert progress[LEMMA_IDS["casa"]].correct_count >= 1


def test_lemma_list_is_paged_and_searchable(
    authenticated_client: TestClient,
) -> None:
    page = authenticated_client.get("/lemmas/", params={"language": "pt"})
    assert page.status_code == 200
    assert "of 6 lemma(s)" in page.text
    partial = authenticated_client.get("/lemmas/partial", params={"q": "agu"})
    assert "água" in partial.text
    assert "casa" not in partial.text


def test_lemma_detail_lists_meanings_and_translations(
    authenticated_client: TestClient,
) -> None:
    page = authenticated_client.get(f"/lemmas/{LEMMA_IDS['casa']}")
    assert page.status_code == 200
    assert "a building to live in" in page.text
    assert "house" in page.text
    assert "A casa é grande." in page.text
    missing = authenticated_client.get("/lemmas/does-not-exist")
    assert "Lemma not found" in missing.text
