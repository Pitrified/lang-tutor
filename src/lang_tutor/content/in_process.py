"""In-process content source.

Reads content directly from the `lang-tools` lexicon store in the same process.
This is the phase-2 coupling, kept available for local/dev where running the
HTTP service is unnecessary. The HTTP source is the default in deployed setups.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lang_tools.lexicon import count_lemmas_filtered
from lang_tools.lexicon import get_lemma_by_id as _store_get_lemma_by_id
from lang_tools.lexicon import get_lemmas_filtered
from lang_tools.lexicon import lemma_card
from lang_tools.lexicon import lemma_cards
from lang_tools.lexicon import lemma_sense_cards

from lang_tutor.content.base import ContentSource
from lang_tutor.content.base import LemmaPage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from lang_tools.lexicon import CardQuery
    from lang_tools.lexicon import Lemma
    from lang_tools.lexicon import LemmaCard


class InProcessContentSource(ContentSource):
    """Content source backed by the in-process `lang-tools` lexicon store."""

    def get_cards(self, query: CardQuery) -> list[LemmaCard]:
        """Return up to ``query.limit`` drill cards matching the filters."""
        return lemma_cards(query)

    def get_card(
        self,
        lemma_id: str,
        *,
        gloss_language: str = "en",
        translation_languages: Sequence[str] = ("en",),
        known_languages: Sequence[str] = (),
    ) -> LemmaCard | None:
        """Return the drill card of one lemma, or None if absent."""
        return lemma_card(
            lemma_id,
            gloss_language=gloss_language,
            translation_languages=translation_languages,
            known_languages=known_languages,
        )

    def get_sense_cards(
        self,
        lemma_id: str,
        *,
        gloss_language: str = "en",
        translation_languages: Sequence[str] = ("en",),
        known_languages: Sequence[str] = (),
    ) -> list[LemmaCard]:
        """Return one card per sense of a lemma, best sense first."""
        return lemma_sense_cards(
            lemma_id,
            gloss_language=gloss_language,
            translation_languages=translation_languages,
            known_languages=known_languages,
        )

    def get_lemma_page(
        self,
        *,
        language: str | None = None,
        topic: str | None = None,
        query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> LemmaPage:
        """Return one page of lemmas and the total match count."""
        lemmas = get_lemmas_filtered(
            language=language,
            topic=topic,
            query=query,
            limit=limit,
            offset=offset,
        )
        total = count_lemmas_filtered(language=language, topic=topic, query=query)
        return LemmaPage(lemmas=lemmas, total=total)

    def get_lemma_by_id(self, lemma_id: str) -> Lemma | None:
        """Return a single lemma by its deterministic id, or None if absent."""
        return _store_get_lemma_by_id(lemma_id)
