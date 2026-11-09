"""Tests for the sentence reconstruction prompt."""

from lang_tools.lexicon import Lemma
from lang_tools.lexicon import LemmaCard

from lang_tutor.webapp.api.v1.exercises_api import _sentence_hint


def test_hint_adds_the_form_note() -> None:
    card = LemmaCard(
        lemma=Lemma(text="são", language="pt", part_of_speech="verb"),
        gloss="have the quality of being",
        translations={"en": ["be"]},
        form_note='3rd person plural present of "ser": they are',
    )
    assert _sentence_hint(card, "en") == (
        'A sentence with “são” (be; 3rd person plural present of "ser": they are)'
    )


def test_hint_without_a_form_note() -> None:
    card = LemmaCard(
        lemma=Lemma(text="casa", language="pt", part_of_speech="noun"),
        gloss="a building to live in",
        translations={"en": ["house"]},
    )
    assert _sentence_hint(card, "en") == "A sentence with “casa” (house)"
