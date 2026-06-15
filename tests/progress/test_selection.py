"""Tests for `lang_tutor.progress.selection`."""

import random

from lang_tools.lexicon.lemma import Lemma

from lang_tutor.progress.progress import UserLemmaProgress
from lang_tutor.progress.selection import LemmaFilter
from lang_tutor.progress.selection import SelectionWeights
from lang_tutor.progress.selection import compute_weight
from lang_tutor.progress.selection import select_lemmas


def _lemma(text: str = "amor", **extra: object) -> Lemma:
    return Lemma(
        text=text,
        language="pt",
        part_of_speech="noun",
        frequency="medium",
        **extra,  # type: ignore[arg-type]
    )


def test_useless_lemmas_get_zero_weight() -> None:
    lemma = _lemma()
    progress = UserLemmaProgress(user_id="u", lemma_id=lemma.id, is_useless=True)
    assert compute_weight(lemma, progress, SelectionWeights()) == 0.0


def test_unseen_lemmas_have_higher_weight_than_seen() -> None:
    seen_lemma = _lemma("paz")
    unseen_lemma = _lemma("amor")
    seen_progress = UserLemmaProgress(
        user_id="u", lemma_id=seen_lemma.id, seen_count=10,
    )
    unseen_progress = UserLemmaProgress(user_id="u", lemma_id=unseen_lemma.id)
    weights = SelectionWeights()
    assert compute_weight(unseen_lemma, unseen_progress, weights) > compute_weight(
        seen_lemma, seen_progress, weights,
    )


def test_lemma_filter_min_length() -> None:
    short = _lemma("oi")
    long_lemma = _lemma("paciencia")
    f = LemmaFilter(min_length=4)
    assert not f.matches(short)
    assert f.matches(long_lemma)


def test_select_lemmas_returns_distinct() -> None:
    pool = [_lemma(t) for t in ("amor", "paz", "luz", "vida", "sol")]
    progress: dict[str, UserLemmaProgress] = {}
    rng = random.Random(0)
    chosen = select_lemmas(pool, progress, n=3, rng=rng)
    assert len(chosen) == 3
    assert len({lemma.id for lemma in chosen}) == 3
