"""Tests for ContentParams environment loading."""

import pytest

from lang_tutor.params.content_params import ContentParams
from lang_tutor.params.content_params import UnknownContentSourceError


def test_defaults_to_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """With no env set, the source defaults to http."""
    monkeypatch.delenv("LANG_TOOLS_CONTENT_SOURCE", raising=False)
    monkeypatch.delenv("LANG_TOOLS_BASE_URL", raising=False)
    params = ContentParams()
    assert params.source == "http"
    assert params.base_url == "http://localhost:8010"


def test_in_process_source(monkeypatch: pytest.MonkeyPatch) -> None:
    """The in_process source is selectable via env."""
    monkeypatch.setenv("LANG_TOOLS_CONTENT_SOURCE", "in_process")
    params = ContentParams()
    assert params.source == "in_process"


def test_source_is_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    """The source value is normalised to lower case."""
    monkeypatch.setenv("LANG_TOOLS_CONTENT_SOURCE", "HTTP")
    assert ContentParams().source == "http"


def test_base_url_trailing_slash_stripped(monkeypatch: pytest.MonkeyPatch) -> None:
    """A trailing slash on the base URL is stripped."""
    monkeypatch.setenv("LANG_TOOLS_BASE_URL", "http://example.com:9000/")
    assert ContentParams().base_url == "http://example.com:9000"


def test_unknown_source_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unsupported source value raises a descriptive error."""
    monkeypatch.setenv("LANG_TOOLS_CONTENT_SOURCE", "carrier-pigeon")
    with pytest.raises(UnknownContentSourceError, match="carrier-pigeon"):
        ContentParams()
