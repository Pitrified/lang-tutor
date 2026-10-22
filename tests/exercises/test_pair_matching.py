"""Tests for `lang_tutor.exercises.pair_matching`."""

import random

from lang_tools.lexicon import Lemma
from lang_tools.lexicon import LemmaCard
import pytest

from lang_tutor.exercises.pair_matching import MissingTranslationError
from lang_tutor.exercises.pair_matching import PairMatchingExercise


def _card(text: str, translations: dict[str, list[str]]) -> LemmaCard:
    return LemmaCard(
        lemma=Lemma(text=text, language="pt", part_of_speech="noun"),
        translations=translations,
    )


def test_pair_matching_correct_pair() -> None:
    cards = [_card("amor", {"en": ["love"]}), _card("paz", {"en": ["peace"]})]
    ex = PairMatchingExercise(target_language="en", rng=random.Random(0))
    round_ = ex.start(cards)
    result = ex.submit(round_, ("amor", "love"))
    assert result.correct is True
    assert result.lemma_results[0].lemma_id == cards[0].lemma.id


def test_pair_matching_wrong_pair() -> None:
    cards = [_card("amor", {"en": ["love"]}), _card("paz", {"en": ["peace"]})]
    ex = PairMatchingExercise(target_language="en", rng=random.Random(0))
    round_ = ex.start(cards)
    result = ex.submit(round_, ("amor", "peace"))
    assert result.correct is False


def test_shared_translation_takes_the_next_one() -> None:
    """Two cards never show the same right-hand word."""
    cards = [
        _card("casa", {"en": ["house", "home"]}),
        _card("lar", {"en": ["House", "hearth"]}),
    ]
    ex = PairMatchingExercise(target_language="en", rng=random.Random(0))
    pairs = ex.start(cards).expected["pairs"]
    assert pairs == {"casa": "house", "lar": "hearth"}


def test_card_without_an_unused_translation_is_dropped() -> None:
    cards = [
        _card("casa", {"en": ["house"]}),
        _card("moradia", {"en": ["house"]}),
        _card("paz", {"en": ["peace"]}),
        _card("luz", {"en": ["light"]}),
    ]
    ex = PairMatchingExercise(target_language="en", rng=random.Random(0))
    pairs = ex.start(cards, num_pairs=2).expected["pairs"]
    assert pairs == {"casa": "house", "paz": "peace"}


def test_missing_translation_raises() -> None:
    ex = PairMatchingExercise(target_language="en", rng=random.Random(0))
    with pytest.raises(MissingTranslationError):
        ex.start([_card("amor", {"fr": ["amour"]})])
