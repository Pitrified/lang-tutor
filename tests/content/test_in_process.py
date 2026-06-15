"""Tests for the in-process content source."""

from lang_tutor.content.in_process import InProcessContentSource


def test_get_lemmas_filtered_returns_lemmas() -> None:
    """The in-process source reads lemmas from the lang-tools store."""
    source = InProcessContentSource()
    lemmas = source.get_lemmas_filtered(language="pt")
    assert lemmas
    assert all(lemma.language == "pt" for lemma in lemmas)


def test_get_lemma_by_id_round_trip() -> None:
    """A lemma fetched by filter can be re-fetched by its id."""
    source = InProcessContentSource()
    known = source.get_lemmas_filtered(language="pt")[0]
    fetched = source.get_lemma_by_id(known.id)
    assert fetched is not None
    assert fetched.id == known.id


def test_get_lemma_by_id_missing_returns_none() -> None:
    """An unknown id resolves to None."""
    source = InProcessContentSource()
    assert source.get_lemma_by_id("does-not-exist") is None
