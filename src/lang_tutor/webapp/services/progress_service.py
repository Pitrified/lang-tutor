"""Session-only learner progress.

Holds one `UserLemmaProgress` per (user, lemma) **in memory**, so weighted
selection prefers unseen and error-heavy lemmas within a server process. It is
not persisted: a restart forgets it. A durable store is its own follow-up
(see ``lang-tools`` ``scratch_space/09_concept_model/09_sample_and_consumer.md``,
Q2); this module is the seam it will replace.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lang_tutor.progress.progress import UserLemmaProgress

if TYPE_CHECKING:
    from lang_tutor.exercises.base import ExerciseType
    from lang_tutor.exercises.base import LemmaResult
    from lang_tutor.exercises.base import ProgressCallback


class SessionProgressService:
    """In-memory per-user progress, fed by the exercises' progress callbacks."""

    def __init__(self) -> None:
        """Start with no recorded progress."""
        self._by_user: dict[str, dict[str, UserLemmaProgress]] = {}

    def for_user(self, user_id: str) -> dict[str, UserLemmaProgress]:
        """Return the user's progress map, keyed by lemma id (live, not a copy).

        Args:
            user_id: Opaque user identifier.

        Returns:
            The ``lemma_id -> UserLemmaProgress`` map (empty for a new user).
        """
        return self._by_user.setdefault(user_id, {})

    def recorder(self, user_id: str, exercise_type: ExerciseType) -> ProgressCallback:
        """Return a progress callback that records results for one user.

        Args:
            user_id: Opaque user identifier.
            exercise_type: Tag recorded in each lemma's per-exercise stats.

        Returns:
            A callback to pass as an exercise's ``progress_callback``.
        """

        def _record(results: list[LemmaResult]) -> None:
            progress = self.for_user(user_id)
            for result in results:
                record = progress.setdefault(
                    result.lemma_id,
                    UserLemmaProgress(user_id=user_id, lemma_id=result.lemma_id),
                )
                record.record(correct=result.correct, exercise_type=exercise_type)

        return _record


_service = SessionProgressService()


def get_progress_service() -> SessionProgressService:
    """Return the process-wide session progress service."""
    return _service
