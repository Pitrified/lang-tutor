"""Tests for `lang_tutor.exercises.diacritic_typing`."""

from lang_tools.lexicon import Lemma
from lang_tools.lexicon import LemmaCard

from lang_tutor.exercises.diacritic_typing import DiacriticTypingExercise


def _card() -> LemmaCard:
    return LemmaCard(
        lemma=Lemma(text="café", language="fr", part_of_speech="noun"),
        gloss="a hot drink",
        translations={"en": ["coffee", "java"]},
    )


def test_prompt_carries_the_meaning_hints() -> None:
    round_ = DiacriticTypingExercise().start(_card())
    assert round_.prompt["glosses"] == ["a hot drink"]
    assert round_.prompt["translation"] == "coffee"
    assert round_.prompt["display"] == ["_"] * 4


def test_diacritic_typing_correct_keystroke() -> None:
    ex = DiacriticTypingExercise()
    round_ = ex.start(_card())
    result = ex.submit(round_, "c")
    assert result.correct is True


def test_diacritic_typing_wrong_keystroke_disables() -> None:
    ex = DiacriticTypingExercise()
    round_ = ex.start(_card())
    result = ex.submit(round_, "z")
    assert result.correct is False
    assert "z" in round_.prompt["disabled_keys"]


def test_diacritic_typing_completion_emits_lemma_result() -> None:
    ex = DiacriticTypingExercise()
    round_ = ex.start(_card())
    results = [ex.submit(round_, ch) for ch in "café"]
    final = results[-1]
    assert final.lemma_results
    assert final.lemma_results[0].correct is True
