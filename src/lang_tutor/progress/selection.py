"""Weighted random selection over a pool of drill cards.

Merges the `brazilian-bites` and `go-accenter` heuristics:

- Errors strongly boost weight.
- Unseen lemmas receive the maximum priority.
- Easier lemmas (by the best sense's CEFR band) get a mild bonus.
- A false friend of a word the learner knows gets a mild bonus (worth
  practising); a cognate of one gets a mild damping (free vocabulary). Both read
  `LemmaCard.lookalikes`, so they apply when the card query names the learner's
  known languages.
- Recently-seen lemmas decay.
- Lemmas flagged `is_useless` are excluded entirely.

The pool is a list of `lang_tools.lexicon.LemmaCard`. Filtering (language,
level, word shape, translations) is the `CardQuery`'s job on the `lang-tools`
side; this module only weights what comes back. `draw_cards` ties the two
together: it asks the content source for a candidate window a few times the
round size, then weights that window with the user's progress.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
import random
from typing import TYPE_CHECKING

from lang_tools.lexicon.card import MAX_CARD_LIMIT

if TYPE_CHECKING:
    from collections.abc import Iterable

    from lang_tools.lexicon import CardQuery
    from lang_tools.lexicon import LemmaCard

    from lang_tutor.content.base import ContentSource
    from lang_tutor.progress.progress import UserLemmaProgress


#: Mild per-band multipliers: easier (and so more common) meanings come up a
#: little more often. An unknown band scores like B2.
_LEVEL_FACTOR: dict[str, float] = {
    "A1": 1.3,
    "A2": 1.2,
    "B1": 1.1,
    "B2": 1.0,
    "C1": 0.9,
    "C2": 0.8,
}

#: How many candidates `draw_cards` fetches per card it returns.
DEFAULT_WINDOW_FACTOR = 4


@dataclass
class SelectionWeights:
    """Tunable knobs for the weighting algorithm.

    Attributes:
        base: Weight assigned to a freshly-seen lemma with no errors.
        error_boost: Multiplier per recorded error.
        unseen_multiplier: Multiplier applied when `seen_count == 0`.
        recency_half_life_seconds: Time-to-half-weight after a recent encounter.
        level_factor: Per-CEFR-band multipliers.
        trap_factor: Multiplier for a false friend of a known word.
        cognate_factor: Multiplier for a cognate of a known word (no trap).
    """

    base: float = 1.0
    error_boost: float = 3.0
    unseen_multiplier: float = 5.0
    recency_half_life_seconds: float = 3600.0  # 1 hour
    level_factor: dict[str, float] = field(
        default_factory=lambda: dict(_LEVEL_FACTOR),
    )
    trap_factor: float = 1.3
    cognate_factor: float = 0.7


def compute_weight(
    card: LemmaCard,
    progress: UserLemmaProgress | None,
    weights: SelectionWeights | None = None,
    *,
    now: datetime | None = None,
) -> float:
    """Return the selection weight for one ``(card, progress)`` pair.

    Args:
        card: The drill card being scored.
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

    # Level factor.
    if card.cefr_level is not None:
        weight *= weights.level_factor.get(card.cefr_level, 1.0)

    # Look-alikes in the learner's known languages.
    if card.is_trap:
        weight *= weights.trap_factor
    elif card.has_cognate:
        weight *= weights.cognate_factor

    # Recency decay: halves every `recency_half_life_seconds` since last seen.
    if progress is not None and progress.last_seen_at is not None:
        now = now if now is not None else datetime.now()  # noqa: DTZ005
        elapsed = max(0.0, (now - progress.last_seen_at).total_seconds())
        weight *= 1.0 - 0.5 ** (elapsed / weights.recency_half_life_seconds)

    return max(0.0, weight)


def select_lemmas(
    pool: Iterable[LemmaCard],
    progress: dict[str, UserLemmaProgress],
    n: int,
    *,
    weights: SelectionWeights | None = None,
    rng: random.Random | None = None,
    now: datetime | None = None,
) -> list[LemmaCard]:
    """Pick `n` distinct cards from `pool` via weighted sampling.

    Args:
        pool: Candidate cards (any iterable; consumed once).
        progress: Map of `Lemma.id` to `UserLemmaProgress`.
        n: Number of cards to return. Capped at the number of eligible cards.
        weights: Tunable scoring knobs.
        rng: Optional `random.Random` for deterministic tests.
        now: Reference time for recency decay.

    Returns:
        Up to `n` distinct cards ordered by their (random) draw.
    """
    rng = rng or random.SystemRandom()
    candidates: list[tuple[LemmaCard, float]] = []
    seen_ids: set[str] = set()
    for card in pool:
        if card.lemma.id in seen_ids:
            continue
        seen_ids.add(card.lemma.id)
        weight = compute_weight(card, progress.get(card.lemma.id), weights, now=now)
        if weight > 0.0:
            candidates.append((card, weight))

    if not candidates or n <= 0:
        return []

    n = min(n, len(candidates))
    chosen: list[LemmaCard] = []
    remaining = list(candidates)
    for _ in range(n):
        cards, weight_values = zip(*remaining, strict=True)
        index = rng.choices(range(len(cards)), weights=weight_values, k=1)[0]
        chosen.append(cards[index])
        remaining.pop(index)
    return chosen


def draw_cards(
    source: ContentSource,
    query: CardQuery,
    progress: dict[str, UserLemmaProgress],
    n: int,
    *,
    window_factor: int = DEFAULT_WINDOW_FACTOR,
    weights: SelectionWeights | None = None,
    rng: random.Random | None = None,
) -> list[LemmaCard]:
    """Fetch a candidate window from the content source and weight it.

    The window is ``n * window_factor`` cards (capped at the service maximum),
    sampled at random by `lang-tools`. Lemmas the user flagged useless are
    excluded on the server side, so they do not take window slots.

    Args:
        source: The content source to read cards from.
        query: The round's card filters; its ``limit`` is replaced.
        progress: Map of `Lemma.id` to `UserLemmaProgress`.
        n: Number of cards to return.
        window_factor: Candidates fetched per returned card.
        weights: Tunable scoring knobs.
        rng: Optional `random.Random` for deterministic tests.

    Returns:
        Up to `n` distinct cards.
    """
    useless = [lid for lid, record in progress.items() if record.is_useless]
    window = query.model_copy(
        update={
            "limit": max(1, min(n * window_factor, MAX_CARD_LIMIT)),
            "exclude_ids": [*query.exclude_ids, *useless],
        },
    )
    return select_lemmas(
        source.get_cards(window),
        progress,
        n,
        weights=weights,
        rng=rng,
    )
