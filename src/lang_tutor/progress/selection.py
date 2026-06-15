"""Weighted random selection over a `Lemma` pool.

Merges the `brazilian-bites` and `go-accenter` heuristics:

- Errors strongly boost weight.
- Unseen lemmas receive the maximum priority.
- High-frequency lemmas get a mild bonus.
- Recently-seen lemmas decay.
- Lemmas flagged `is_useless` are excluded entirely.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
import random
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import Iterable

    from lang_tools.lexicon.lemma import Lemma

    from lang_tutor.progress.progress import UserLemmaProgress


_FREQUENCY_FACTOR: dict[str, float] = {
    "high": 1.2,
    "medium": 1.0,
    "low": 0.8,
}


class LemmaFilter(BaseModel):
    """Optional pool filter applied before weighted selection.

    Attributes:
        has_accent: Restrict to lemmas whose `text` contains accented chars.
        has_translation: Require a translation in this target language code.
        min_length: Minimum `len(text)`.
        max_length: Maximum `len(text)`.
        topics: At least one of these topics must be present (if non-empty).
        languages: Restrict to lemmas in any of these ISO 639-1 codes.
    """

    has_accent: bool | None = None
    has_translation: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    topics: list[str] | None = None
    languages: list[str] | None = None

    def matches(self, lemma: Lemma) -> bool:
        """Return True if `lemma` passes every active constraint."""
        if self.has_accent is not None and lemma.has_accent != self.has_accent:
            return False
        if (
            self.has_translation is not None
            and self.has_translation not in lemma.translations
        ):
            return False
        if self.min_length is not None and lemma.length < self.min_length:
            return False
        if self.max_length is not None and lemma.length > self.max_length:
            return False
        if self.topics and not set(self.topics).intersection(lemma.topics):
            return False
        return not (self.languages and lemma.language not in self.languages)


@dataclass
class SelectionWeights:
    """Tunable knobs for the weighting algorithm.

    Attributes:
        base: Weight assigned to a freshly-seen lemma with no errors.
        error_boost: Multiplier per recorded error.
        unseen_multiplier: Multiplier applied when `seen_count == 0`.
        recency_half_life_seconds: Time-to-half-weight after a recent encounter.
        frequency_factor: Per-frequency-tier multipliers.
    """

    base: float = 1.0
    error_boost: float = 3.0
    unseen_multiplier: float = 5.0
    recency_half_life_seconds: float = 3600.0  # 1 hour
    frequency_factor: dict[str, float] = field(
        default_factory=lambda: dict(_FREQUENCY_FACTOR),
    )


def compute_weight(
    lemma: Lemma,
    progress: UserLemmaProgress | None,
    weights: SelectionWeights | None = None,
    *,
    now: datetime | None = None,
) -> float:
    """Return the selection weight for one ``(lemma, progress)`` pair.

    Args:
        lemma: The lemma being scored.
        progress: Progress record, or ``None`` if the user has never seen it.
        weights: Tunable scoring knobs; defaults to `SelectionWeights()`.
        now: Reference timestamp for recency decay; defaults to
            ``datetime.now()``.

    Returns:
        Non-negative weight. ``0.0`` when the lemma is flagged `is_useless`.
    """
    weights = weights or SelectionWeights()

    if progress is not None and progress.is_useless:
        return 0.0

    weight = weights.base

    # Unseen boost vs error boost (apply one or the other, not both).
    if progress is None or progress.seen_count == 0:
        weight *= weights.unseen_multiplier
    else:
        weight *= 1.0 + weights.error_boost * progress.error_count

    # Frequency factor.
    if lemma.frequency is not None:
        weight *= weights.frequency_factor.get(lemma.frequency, 1.0)

    # Recency decay: halves every `recency_half_life_seconds` since last seen.
    if progress is not None and progress.last_seen_at is not None:
        now = now if now is not None else datetime.now()  # noqa: DTZ005
        elapsed = max(0.0, (now - progress.last_seen_at).total_seconds())
        weight *= 1.0 - 0.5 ** (elapsed / weights.recency_half_life_seconds)

    return max(0.0, weight)


def select_lemmas(
    pool: Iterable[Lemma],
    progress: dict[str, UserLemmaProgress],
    n: int,
    *,
    lemma_filter: LemmaFilter | None = None,
    weights: SelectionWeights | None = None,
    rng: random.Random | None = None,
    now: datetime | None = None,
) -> list[Lemma]:
    """Pick `n` distinct lemmas from `pool` via weighted sampling.

    Args:
        pool: Candidate lemmas (any iterable; consumed once).
        progress: Map of `Lemma.id` to `UserLemmaProgress`.
        n: Number of lemmas to return. Capped at the number of eligible lemmas.
        lemma_filter: Optional `LemmaFilter` applied before weighting.
        weights: Tunable scoring knobs.
        rng: Optional `random.Random` for deterministic tests.
        now: Reference time for recency decay.

    Returns:
        Up to `n` distinct `Lemma` instances ordered by their (random) draw.
    """
    rng = rng or random.SystemRandom()
    candidates: list[tuple[Lemma, float]] = []
    for lemma in pool:
        if lemma_filter is not None and not lemma_filter.matches(lemma):
            continue
        weight = compute_weight(lemma, progress.get(lemma.id), weights, now=now)
        if weight > 0.0:
            candidates.append((lemma, weight))

    if not candidates or n <= 0:
        return []

    n = min(n, len(candidates))
    chosen: list[Lemma] = []
    remaining = list(candidates)
    for _ in range(n):
        lemmas, weight_values = zip(*remaining, strict=True)
        index = rng.choices(range(len(lemmas)), weights=weight_values, k=1)[0]
        chosen.append(lemmas[index])
        remaining.pop(index)
    return chosen
