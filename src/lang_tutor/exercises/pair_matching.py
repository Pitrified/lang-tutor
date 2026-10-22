"""Pair matching exercise (from `brazilian-bites`).

Given N drill cards, the user matches each lemma to its translation drawn from
a shuffled column. Each `submit` call evaluates a single ``(left, right)`` tap.

The translation is the most frequent target-language lemma of the card's best
sense (`LemmaCard.translations`). Two cards that would show the same right-hand
word make the round ambiguous, so a card takes its next translation instead,
and a card with no unused translation left is dropped from the round.
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
    from lang_tools.lexicon import Lemma
    from lang_tools.lexicon import LemmaCard


class MissingTranslationError(KeyError):
    """Raised when no card carries a usable translation in the target language."""

    def __init__(self, lemma: Lemma, target_language: str) -> None:
        """Initialize with the offending lemma and the missing target language.

        Args:
            lemma: The lemma that lacks a translation.
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
            target_language: ISO 639-1 code used to look up
                `LemmaCard.translations`.
            rng: Optional `random.Random`; defaults to `random.SystemRandom`.
            **kwargs: Forwarded to `_BaseExercise`.
        """
        super().__init__(exercise_type="pair_matching", **kwargs)  # type: ignore[arg-type]
        self.target_language = target_language
        self.rng = rng or random.SystemRandom()

    def start(
        self,
        cards: list[LemmaCard],
        *,
        num_pairs: int | None = None,
    ) -> ExerciseRound:
        """Build a round from a list of drill cards.

        Args:
            cards: Candidate cards, in draw order. Pass a few more than
                ``num_pairs`` so a dropped card does not shrink the round.
            num_pairs: Stop once this many pairs are built; every usable card
                when None.

        Returns:
            `ExerciseRound` whose `prompt` carries the left/right columns and
            `expected` the correct mapping ``{left_text: right_text}``.

        Raises:
            MissingTranslationError: When no card yields a pair (every card
                lacks an unused translation in `target_language`).
        """
        self._ensure_started()
        pairs: dict[str, str] = {}
        lemma_by_text: dict[str, Lemma] = {}
        used: set[str] = set()
        for card in cards:
            if num_pairs is not None and len(pairs) >= num_pairs:
                break
            if card.lemma.text in pairs:
                continue
            options = card.translations.get(self.target_language, [])
            translation = next((t for t in options if t.casefold() not in used), None)
            if translation is None:
                continue
            used.add(translation.casefold())
            pairs[card.lemma.text] = translation
            lemma_by_text[card.lemma.text] = card.lemma
        if not pairs:
            raise MissingTranslationError(cards[0].lemma, self.target_language)

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
