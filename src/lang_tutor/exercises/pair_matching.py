"""Pair matching exercise (from `brazilian-bites`).

Given N lemmas, the user matches each one to its translation drawn from a
shuffled column. Each `submit` call evaluates a single ``(left, right)`` tap.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import random
from typing import TYPE_CHECKING

from lang_tutor.exercises.base import ExerciseRound
from lang_tutor.exercises.base import LemmaResult
from lang_tutor.exercises.base import RoundResult
from lang_tutor.exercises.base import _BaseExercise

if TYPE_CHECKING:
    from lang_tools.lexicon.lemma import Lemma


class MissingTranslationError(KeyError):
    """Raised when a lemma does not carry a translation in the target language."""

    def __init__(self, lemma: Lemma, target_language: str) -> None:
        """Initialize with the offending lemma and the missing target language.

        Args:
            lemma: The `Lemma` that lacks a translation.
            target_language: Target ISO 639-1 code that was requested.
        """
        super().__init__(
            f"Lemma {lemma.text!r} has no translation in {target_language!r}",
        )
        self.lemma = lemma
        self.target_language = target_language


@dataclass
class PairMatchingExercise(_BaseExercise):
    """Pair-matching round factory.

    Attributes:
        target_language: ISO 639-1 code for the translations side.
        rng: Optional `random.Random` for deterministic shuffles.
    """

    target_language: str = "en"
    rng: random.Random = field(default_factory=random.SystemRandom)

    def __init__(
        self,
        target_language: str = "en",
        rng: random.Random | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize with the translation language and an optional RNG.

        Args:
            target_language: ISO 639-1 code used to look up `Lemma.translations`.
            rng: Optional `random.Random`; defaults to `random.SystemRandom`.
            **kwargs: Forwarded to `_BaseExercise`.
        """
        super().__init__(exercise_type="pair_matching", **kwargs)  # type: ignore[arg-type]
        self.target_language = target_language
        self.rng = rng or random.SystemRandom()

    def start(self, lemmas: list[Lemma]) -> ExerciseRound:
        """Build a round from a list of lemmas.

        Args:
            lemmas: The lemmas to match. Each must have a translation in
                `target_language`.

        Returns:
            `ExerciseRound` whose `prompt` carries the left/right columns and
            `expected` the correct mapping ``{left_text: right_text}``.

        Raises:
            MissingTranslationError: When any lemma lacks a translation in
                `target_language`.
        """
        self._ensure_started()
        pairs: dict[str, str] = {}
        lemma_by_text: dict[str, Lemma] = {}
        for lemma in lemmas:
            translation = lemma.translations.get(self.target_language)
            if translation is None:
                raise MissingTranslationError(lemma, self.target_language)
            pairs[lemma.text] = translation
            lemma_by_text[lemma.text] = lemma

        right_column = list(pairs.values())
        self.rng.shuffle(right_column)
        return ExerciseRound(
            prompt={
                "left_lemmas": list(pairs.keys()),
                "right_lemmas": right_column,
            },
            expected={"pairs": pairs, "lemma_by_text": lemma_by_text},
        )

    def submit(
        self,
        round_: ExerciseRound,
        selected_pair: tuple[str, str],
    ) -> RoundResult:
        """Score a single ``(left_lemma, right_lemma)`` tap.

        Args:
            round_: The round returned by `start`.
            selected_pair: The user's chosen ``(left, right)`` pair.

        Returns:
            `RoundResult` reflecting whether the right value matches the
            expected translation for the left lemma. Includes one `LemmaResult`
            for the left lemma.
        """
        left, right = selected_pair
        expected_pairs: dict[str, str] = round_.expected["pairs"]
        lemma_by_text: dict[str, Lemma] = round_.expected["lemma_by_text"]
        correct = expected_pairs.get(left) == right
        lemma_results: list[LemmaResult] = []
        if left in lemma_by_text:
            lemma_results.append(
                LemmaResult(lemma_id=lemma_by_text[left].id, correct=correct),
            )
        result = RoundResult(
            correct=correct,
            feedback=None if correct else "Wrong pair.",
            lemma_results=lemma_results,
        )
        self._bookkeep(result)
        return result
