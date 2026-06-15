"""In-process content source.

Reads content directly from the `lang-tools` lemma store in the same process.
This is the phase-2 coupling, kept available for local/dev where running the
HTTP service is unnecessary. The HTTP source is the default in deployed setups.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lang_tools.lexicon.lemma_store import get_lemma_by_id as _store_get_lemma_by_id
from lang_tools.lexicon.lemma_store import (
    get_lemmas_filtered as _store_get_lemmas_filtered,
)

from lang_tutor.content.base import ContentSource

if TYPE_CHECKING:
    from lang_tools.lexicon.lemma import Lemma


class InProcessContentSource(ContentSource):
    """Content source backed by the in-process `lang-tools` lemma store."""

    def get_lemmas_filtered(
        self,
        language: str | None = None,
        topic: str | None = None,
    ) -> list[Lemma]:
        """Return lemmas filtered by optional language and/or topic."""
        return _store_get_lemmas_filtered(language=language, topic=topic)

    def get_lemma_by_id(self, lemma_id: str) -> Lemma | None:
        """Return a single lemma by its deterministic id, or None if absent."""
        return _store_get_lemma_by_id(lemma_id)
