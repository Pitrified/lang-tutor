"""In-process content source.

Reads content directly from the `lang-tools` word store in the same process.
This is the phase-2 coupling, kept available for local/dev where running the
HTTP service is unnecessary. The HTTP source is the default in deployed setups.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lang_tools.words.word_store import get_word_by_id as _store_get_word_by_id
from lang_tools.words.word_store import get_words_filtered as _store_get_words_filtered

from lang_tutor.content.base import ContentSource

if TYPE_CHECKING:
    from lang_tools.words.word import Word


class InProcessContentSource(ContentSource):
    """Content source backed by the in-process `lang-tools` word store."""

    def get_words_filtered(
        self,
        language: str | None = None,
        topic: str | None = None,
    ) -> list[Word]:
        """Return words filtered by optional language and/or topic."""
        return _store_get_words_filtered(language=language, topic=topic)

    def get_word_by_id(self, word_id: str) -> Word | None:
        """Return a single word by its deterministic id, or None if absent."""
        return _store_get_word_by_id(word_id)
