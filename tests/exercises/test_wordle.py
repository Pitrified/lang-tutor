"""Tests for `lang_tutor.exercises.wordle`."""

from lang_tools.lexicon.lemma import Lemma

from lang_tutor.exercises.wordle import WordleExercise
from lang_tutor.exercises.wordle import _evaluate


def _lemma(text: str = "amor") -> Lemma:
    return Lemma(text=text, language="pt", part_of_speech="noun")


def test_evaluate_marks_correct_misplaced_wrong() -> None:
    # target="amor", guess="omar": o misplaced, m correct, a misplaced, r correct
    res = _evaluate("omar", "amor")
    states = [r.state for r in res]
    assert states == ["misplaced", "correct", "misplaced", "correct"]


def test_wordle_correct_guess() -> None:
    ex = WordleExercise()
    round_ = ex.start(_lemma("amor"))
    result = ex.submit(round_, "amor")
    assert result.correct is True
    assert result.lemma_results
    assert result.lemma_results[0].correct is True


def test_wordle_wrong_length_rejected() -> None:
    ex = WordleExercise()
    round_ = ex.start(_lemma("amor"))
    result = ex.submit(round_, "am")
    assert result.correct is False


def test_wordle_exhausts_attempts() -> None:
    ex = WordleExercise()
    round_ = ex.start(_lemma("amor"), max_attempts=1)
    result = ex.submit(round_, "vida")
    assert result.correct is False
    assert result.lemma_results
    assert result.lemma_results[0].correct is False
