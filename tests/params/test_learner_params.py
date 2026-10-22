"""Tests for `lang_tutor.params.learner_params`."""

import pytest

from lang_tutor.params.learner_params import LearnerParams


def test_defaults_are_a_pt_learner_who_knows_en_and_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LANG_TUTOR_TARGET_LANGUAGE", raising=False)
    monkeypatch.delenv("LANG_TUTOR_KNOWN_LANGUAGES", raising=False)
    params = LearnerParams()
    assert params.target_language == "pt"
    assert params.known_languages == ["en", "it"]


def test_known_languages_parse_and_skip_the_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LANG_TUTOR_TARGET_LANGUAGE", "PT")
    monkeypatch.setenv("LANG_TUTOR_KNOWN_LANGUAGES", " en, ES ,pt,, fr")
    params = LearnerParams()
    assert params.known_languages == ["en", "es", "fr"]
    assert "known_languages: en, es, fr" in str(params)
