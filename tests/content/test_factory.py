"""Tests for the content source factory selection."""

import pytest

from lang_tutor.content import factory
from lang_tutor.content.http import HttpContentSource
from lang_tutor.content.in_process import InProcessContentSource
from lang_tutor.metaclasses.singleton import Singleton


@pytest.fixture(autouse=True)
def _reset_state() -> None:
    """Clear the cached source and params singleton around each test."""
    factory.set_content_source(None)
    Singleton._instances.clear()  # noqa: SLF001


def test_factory_builds_http_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """The default selection is the HTTP source."""
    monkeypatch.delenv("LANG_TOOLS_CONTENT_SOURCE", raising=False)
    source = factory.get_content_source()
    assert isinstance(source, HttpContentSource)


def test_factory_builds_in_process(monkeypatch: pytest.MonkeyPatch) -> None:
    """The in_process selection yields the in-process source."""
    monkeypatch.setenv("LANG_TOOLS_CONTENT_SOURCE", "in_process")
    source = factory.get_content_source()
    assert isinstance(source, InProcessContentSource)


def test_factory_caches_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    """The source is built once and reused."""
    monkeypatch.setenv("LANG_TOOLS_CONTENT_SOURCE", "in_process")
    first = factory.get_content_source()
    second = factory.get_content_source()
    assert first is second


def test_set_content_source_override() -> None:
    """An explicit override is returned without consulting params."""
    override = InProcessContentSource()
    factory.set_content_source(override)
    assert factory.get_content_source() is override
