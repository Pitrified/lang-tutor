"""Tests for `lang_tutor.exercises.pair_matching`."""

import random

from lang_tools.lexicon.lemma import Lemma
import pytest

from lang_tutor.exercises.pair_matching import MissingTranslationError
from lang_tutor.exercises.pair_matching import PairMatchingExercise


def _lemma(text: str, translations: dict[str, str]) -> Lemma:
    return Lemma(
        text=text,
        language="pt",
        part_of_speech="noun",
        frequency="medium",
        translations=translations,
    )


def test_pair_matching_correct_pair() -> None:
    lemmas = [_lemma("amor", {"en": "love"}), _lemma("paz", {"en": "peace"})]
    ex = PairMatchingExercise(target_language="en", rng=random.Random(0))
    round_ = ex.start(lemmas)
    result = ex.submit(round_, ("amor", "love"))
    assert result.correct is True


def test_pair_matching_wrong_pair() -> None:
    lemmas = [_lemma("amor", {"en": "love"}), _lemma("paz", {"en": "peace"})]
    ex = PairMatchingExercise(target_language="en", rng=random.Random(0))
    round_ = ex.start(lemmas)
    result = ex.submit(round_, ("amor", "peace"))
    assert result.correct is False


def test_missing_translation_raises() -> None:
    ex = PairMatchingExercise(target_language="en", rng=random.Random(0))
    with pytest.raises(MissingTranslationError):
        ex.start([_lemma("amor", {"fr": "amour"})])
