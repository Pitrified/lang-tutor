"""Tests for the in-process content source."""

from lang_tutor.content.in_process import InProcessContentSource


def test_get_words_filtered_returns_words() -> None:
    """The in-process source reads words from the lang-tools store."""
    source = InProcessContentSource()
    words = source.get_words_filtered(language="pt")
    assert words
    assert all(w.language == "pt" for w in words)


def test_get_word_by_id_round_trip() -> None:
    """A word fetched by filter can be re-fetched by its id."""
    source = InProcessContentSource()
    known = source.get_words_filtered(language="pt")[0]
    fetched = source.get_word_by_id(known.id)
    assert fetched is not None
    assert fetched.id == known.id


def test_get_word_by_id_missing_returns_none() -> None:
    """An unknown id resolves to None."""
    source = InProcessContentSource()
    assert source.get_word_by_id("does-not-exist") is None
