"""Exercise framework: shared interface and per-mechanic implementations.

Public API:
    EXERCISE_TYPES: tuple of supported exercise type strings.
    ExerciseType: literal alias.
    ExerciseRound, RoundResult, WordResult, SessionSummary: shared data shapes.
    SentenceReconstructionExercise, PairMatchingExercise,
    DiacriticTypingExercise, WordleExercise, ConversationalTutorExercise:
    concrete exercise classes.
    HintLevel: literal for diacritic-typing hint levels.
    WordleConfig: configuration for a Wordle exercise session.
"""

from lang_tutor.exercises.base import EXERCISE_TYPES
from lang_tutor.exercises.base import ExerciseRound
from lang_tutor.exercises.base import ExerciseType
from lang_tutor.exercises.base import RoundResult
from lang_tutor.exercises.base import SessionSummary
from lang_tutor.exercises.base import WordResult
from lang_tutor.exercises.conversational_tutor import ConversationalTutorExercise
from lang_tutor.exercises.conversational_tutor import TutorMessage
from lang_tutor.exercises.diacritic_typing import DiacriticTypingExercise
from lang_tutor.exercises.diacritic_typing import HintLevel
from lang_tutor.exercises.pair_matching import PairMatchingExercise
from lang_tutor.exercises.sentence_reconstruction import SentenceReconstructionExercise
from lang_tutor.exercises.wordle import LetterResult
from lang_tutor.exercises.wordle import LetterState
from lang_tutor.exercises.wordle import WordleExercise
from lang_tutor.exercises.wordle_config import WordleConfig

__all__ = [
    "EXERCISE_TYPES",
    "ConversationalTutorExercise",
    "DiacriticTypingExercise",
    "ExerciseRound",
    "ExerciseType",
    "HintLevel",
    "LetterResult",
    "LetterState",
    "PairMatchingExercise",
    "RoundResult",
    "SentenceReconstructionExercise",
    "SessionSummary",
    "TutorMessage",
    "WordResult",
    "WordleConfig",
    "WordleExercise",
]
