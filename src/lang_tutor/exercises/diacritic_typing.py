"""Diacritic typing exercise (from `go-accenter`).

The user types a hidden accented lemma character by character. Each `submit`
evaluates one keystroke; correct characters are revealed, wrong keys are added
to a disabled set. A round is "won" when every position is filled.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Literal

from lang_tools.language.normalization import normalize as _normalize

from lang_tutor.exercises.base import ExerciseRound
from lang_tutor.exercises.base import LemmaResult
from lang_tutor.exercises.base import RoundResult
from lang_tutor.exercises.base import _BaseExercise

if TYPE_CHECKING:
    from lang_tools.lexicon import Lemma
    from lang_tools.lexicon import LemmaCard

HintLevel = Literal["off", "show_unaccented", "show_all"]


def _initial_display(text: str, hint_level: HintLevel) -> list[str]:
    if hint_level == "show_all":
        return list(text)
    if hint_level == "show_unaccented":
        return [
            ch if _normalize(ch) == ch.lower() else "_"
            for ch in text
        ]
    return ["_"] * len(text)


@dataclass
class _DiacriticState:
    lemma: Lemma
    hint_level: HintLevel
    display: list[str]
    disabled_keys: set[str] = field(default_factory=set)
    error_count: int = 0
    cursor: int = 0


@dataclass
class DiacriticTypingExercise(_BaseExercise):
    """Diacritic typing round factory."""

    def __init__(self, **kwargs: object) -> None:
        """Initialize the exercise.

        Args:
            **kwargs: Forwarded to `_BaseExercise` (e.g. `progress_callback`).
        """
        super().__init__(exercise_type="diacritic_typing", **kwargs)  # type: ignore[arg-type]

    def start(
        self,
        card: LemmaCard,
        *,
        hint_level: HintLevel = "off",
        hint_language: str = "en",
    ) -> ExerciseRound:
        """Build a round for a single lemma.

        The prompt carries the meaning hints: the card's gloss and its first
        translation in ``hint_language``.

        Args:
            card: Drill card of the target lemma; the lemma must contain
                accented characters for the exercise to be meaningful.
            hint_level: Initial hint level (see `HintLevel`).
            hint_language: Language of the translation hint.

        Returns:
            `ExerciseRound` whose `expected` is the internal `_DiacriticState`.
        """
        self._ensure_started()
        lemma = card.lemma
        translations = card.translations.get(hint_language, [])
        state = _DiacriticState(
            lemma=lemma,
            hint_level=hint_level,
            display=_initial_display(lemma.text, hint_level),
        )
        # Advance cursor past pre-revealed characters.
        while state.cursor < len(lemma.text) and state.display[state.cursor] != "_":
            state.cursor += 1

        return ExerciseRound(
            prompt={
                "display": state.display.copy(),
                "hint_level": hint_level,
                "disabled_keys": set(),
                "glosses": [card.gloss] if card.gloss else [],
                "translation": translations[0] if translations else "",
            },
            expected=state,
        )

    def submit(self, round_: ExerciseRound, character: str) -> RoundResult:
        """Score a single keystroke.

        Args:
            round_: The round returned by `start`.
            character: The character the user pressed.

        Returns:
            `RoundResult` whose `correct` is True for that keystroke. Once the
            lemma is complete, a `LemmaResult` with overall correctness (no
            errors) is added to `lemma_results`.
        """
        state: _DiacriticState = round_.expected

        if state.cursor >= len(state.lemma.text):
            return RoundResult(correct=True, feedback="Already complete.")

        expected_char = state.lemma.text[state.cursor]
        correct = character == expected_char

        if correct:
            state.display[state.cursor] = expected_char
            state.cursor += 1
            # Skip already-revealed positions.
            while (
                state.cursor < len(state.lemma.text)
                and state.display[state.cursor] != "_"
            ):
                state.cursor += 1
        else:
            state.disabled_keys.add(character)
            state.error_count += 1

        # Update prompt mirror so callers reading `round_.prompt` see live state.
        round_.prompt["display"] = state.display.copy()
        round_.prompt["disabled_keys"] = set(state.disabled_keys)

        lemma_results: list[LemmaResult] = []
        completed = state.cursor >= len(state.lemma.text)
        if completed:
            lemma_results.append(
                LemmaResult(lemma_id=state.lemma.id, correct=state.error_count == 0),
            )

        result = RoundResult(
            correct=correct,
            feedback=(
                None
                if correct
                else f"{character!r} is not at position {state.cursor}."
            ),
            lemma_results=lemma_results,
        )
        self._bookkeep(result)
        return result
