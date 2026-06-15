"""User-progress tracking and weighted lemma selection.

Public API:
    UserLemmaProgress: per-user per-lemma performance record.
    ExerciseStats: per-exercise-type breakdown of progress.
    LemmaFilter: optional pool filter for `select_lemmas`.
    SelectionWeights: tunable weighting factors.
    select_lemmas: weighted random selection over a `Lemma` pool.
    compute_weight: pure scoring function used by the selector.
"""

from lang_tutor.progress.progress import ExerciseStats
from lang_tutor.progress.progress import UserLemmaProgress
from lang_tutor.progress.selection import LemmaFilter
from lang_tutor.progress.selection import SelectionWeights
from lang_tutor.progress.selection import compute_weight
from lang_tutor.progress.selection import select_lemmas

__all__ = [
    "ExerciseStats",
    "LemmaFilter",
    "SelectionWeights",
    "UserLemmaProgress",
    "compute_weight",
    "select_lemmas",
]
