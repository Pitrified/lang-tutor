"""Tests for `lang_tutor.progress.selection`."""

from collections.abc import Sequence
import random

from lang_tools.lexicon import CardQuery
from lang_tools.lexicon import Lemma
from lang_tools.lexicon import LemmaCard

from lang_tutor.content.base import ContentSource
from lang_tutor.content.base import LemmaPage
from lang_tutor.progress.progress import UserLemmaProgress
from lang_tutor.progress.selection import SelectionWeights
from lang_tutor.progress.selection import compute_weight
from lang_tutor.progress.selection import draw_cards
from lang_tutor.progress.selection import select_lemmas


def _card(text: str = "amor", level: str | None = "B1") -> LemmaCard:
    return LemmaCard(
        lemma=Lemma(text=text, language="pt", part_of_speech="noun"),
        cefr_level=level,
    )


class _FakeSource(ContentSource):
    """Records the card query and serves a fixed pool."""

    def __init__(self, cards: list[LemmaCard]) -> None:
        self.cards = cards
        self.queries: list[CardQuery] = []

    def get_cards(self, query: CardQuery) -> list[LemmaCard]:
        self.queries.append(query)
        excluded = set(query.exclude_ids)
        return [c for c in self.cards if c.lemma.id not in excluded][: query.limit]

    def get_card(
        self,
        lemma_id: str,  # noqa: ARG002
        *,
        gloss_language: str = "en",  # noqa: ARG002
        translation_languages: Sequence[str] = ("en",),  # noqa: ARG002
    ) -> LemmaCard | None:
        return None

    def get_sense_cards(
        self,
        lemma_id: str,  # noqa: ARG002
        *,
        gloss_language: str = "en",  # noqa: ARG002
        translation_languages: Sequence[str] = ("en",),  # noqa: ARG002
    ) -> list[LemmaCard]:
        return []

    def get_lemma_page(self, **_kwargs: object) -> LemmaPage:
        return LemmaPage(lemmas=[], total=0)

    def get_lemma_by_id(self, lemma_id: str) -> Lemma | None:  # noqa: ARG002
        return None


def test_useless_lemmas_get_zero_weight() -> None:
    card = _card()
    progress = UserLemmaProgress(user_id="u", lemma_id=card.lemma.id, is_useless=True)
    assert compute_weight(card, progress, SelectionWeights()) == 0.0


def test_unseen_lemmas_have_higher_weight_than_seen() -> None:
    seen = _card("paz")
    unseen = _card("amor")
    seen_progress = UserLemmaProgress(
        user_id="u", lemma_id=seen.lemma.id, seen_count=10
    )
    unseen_progress = UserLemmaProgress(user_id="u", lemma_id=unseen.lemma.id)
    weights = SelectionWeights()
    assert compute_weight(unseen, unseen_progress, weights) > compute_weight(
        seen,
        seen_progress,
        weights,
    )


def test_easier_band_weighs_more() -> None:
    weights = SelectionWeights()
    assert compute_weight(_card("a", "A1"), None, weights) > compute_weight(
        _card("b", "C2"),
        None,
        weights,
    )
    # No band scores neutral, between the two.
    assert compute_weight(_card("c", None), None, weights) == weights.unseen_multiplier


def test_select_lemmas_returns_distinct() -> None:
    pool = [_card(t) for t in ("amor", "paz", "luz", "vida", "sol")]
    progress: dict[str, UserLemmaProgress] = {}
    chosen = select_lemmas(pool, progress, n=3, rng=random.Random(0))
    assert len(chosen) == 3
    assert len({card.lemma.id for card in chosen}) == 3


def test_select_lemmas_dedupes_the_pool() -> None:
    pool = [_card("amor"), _card("amor"), _card("paz")]
    chosen = select_lemmas(pool, {}, n=5, rng=random.Random(0))
    assert sorted(card.lemma.text for card in chosen) == ["amor", "paz"]


def test_draw_cards_fetches_a_window_and_skips_useless() -> None:
    cards = [_card(t) for t in ("amor", "paz", "luz", "vida", "sol")]
    useless = cards[0].lemma.id
    progress = {
        useless: UserLemmaProgress(user_id="u", lemma_id=useless, is_useless=True)
    }
    source = _FakeSource(cards)
    chosen = draw_cards(
        source,
        CardQuery(language="pt", limit=1),
        progress,
        n=2,
        rng=random.Random(0),
    )
    assert len(chosen) == 2
    assert useless not in {card.lemma.id for card in chosen}
    sent = source.queries[-1]
    assert sent.limit == 8  # n * the default window factor of 4
    assert useless in sent.exclude_ids
