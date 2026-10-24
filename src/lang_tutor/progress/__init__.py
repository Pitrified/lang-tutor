"""User-progress tracking and weighted lemma selection.

Public API:
    UserLemmaProgress: per-user per-lemma performance record.
    ExerciseStats: per-exercise-type breakdown of progress.
    SelectionWeights: tunable weighting factors.
    select_lemmas: weighted random selection over a pool of drill cards.
    draw_cards: fetch a candidate window from the content source, then weight it.
    compute_weight: pure scoring function used by the selector.
"""

from lang_tutor.progress.progress import ExerciseStats
from lang_tutor.progress.progress import UserLemmaProgress
from lang_tutor.progress.selection import SelectionWeights
from lang_tutor.progress.selection import compute_weight
from lang_tutor.progress.selection import draw_cards
from lang_tutor.progress.selection import select_lemmas

__all__ = [
    "ExerciseStats",
    "SelectionWeights",
    "UserLemmaProgress",
    "compute_weight",
    "draw_cards",
    "select_lemmas",
]
