"""Content source interface.

`ContentSource` is the single seam through which `lang-tutor` reads lemma
content. It mirrors the frozen `lang_tools.lexicon` read surface so the
in-process and HTTP implementations are drop-in interchangeable; switching
transport is a one-line change in the factory, not a change at every call site.

Two kinds of read go through it:

- **Drill cards** (`get_cards`, `get_card`, `get_sense_cards`): a lemma with
  its best sense's CEFR band, gloss, translations, and examples
  (`lang_tools.lexicon.LemmaCard`), or one card per sense. The exercises are
  built from these; a `CardQuery` keeps every read bounded.
- **Lemma pages** (`get_lemma_page`, `get_lemma_by_id`): the paged browse /
  search behind the lemma pages.

Nothing here returns a whole language: the full corpus holds 324k lemmas.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from lang_tools.lexicon.card import CardQuery
    from lang_tools.lexicon.card import LemmaCard
    from lang_tools.lexicon.lemma import Lemma


@dataclass
class LemmaPage:
    """One page of a filtered lemma listing.

    Attributes:
        lemmas: The lemmas on this page, ordered by their folded form.
        total: How many lemmas match the filters across all pages.
    """

    lemmas: list[Lemma]
    total: int


class ContentSource(ABC):
    """Read-only access to the `lang-tools` lemma content.

    Implementations differ only in transport: an in-process read of the lexicon
    store or an HTTP call to the `lang-tools` read service. Both return the same
    `lang_tools.lexicon` models, so callers are unaware of which one is wired in.
    """

    @abstractmethod
    def get_cards(self, query: CardQuery) -> list[LemmaCard]:
        """Return up to ``query.limit`` drill cards matching the filters.

        Args:
            query: The card filters, order, and page size.

        Returns:
            The matching cards.
        """

    @abstractmethod
    def get_card(
        self,
        lemma_id: str,
        *,
        gloss_language: str = "en",
        translation_languages: Sequence[str] = ("en",),
    ) -> LemmaCard | None:
        """Return the drill card of one lemma.

        Args:
            lemma_id: The lemma's deterministic id.
            gloss_language: Language of the card's gloss.
            translation_languages: Languages to fill the translations with.

        Returns:
            The card, or None when no lemma has the given id.
        """

    @abstractmethod
    def get_sense_cards(
        self,
        lemma_id: str,
        *,
        gloss_language: str = "en",
        translation_languages: Sequence[str] = ("en",),
    ) -> list[LemmaCard]:
        """Return one card per sense of a lemma, best sense first.

        Args:
            lemma_id: The lemma's deterministic id.
            gloss_language: Language of each card's gloss.
            translation_languages: Languages to fill the translations with.

        Returns:
            The cards (empty for an unknown lemma or one with no sense).
        """

    @abstractmethod
    def get_lemma_page(
        self,
        *,
        language: str | None = None,
        topic: str | None = None,
        query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> LemmaPage:
        """Return one page of lemmas filtered by language, topic, and/or prefix.

        Args:
            language: ISO 639-1 code to filter by. No filter when None.
            topic: Topic tag to filter by. No filter when None.
            query: Prefix of the accent- and case-folded form.
            limit: Page size.
            offset: Matches to skip before the page.

        Returns:
            The page and the total match count.
        """

    @abstractmethod
    def get_lemma_by_id(self, lemma_id: str) -> Lemma | None:
        """Return a single lemma by its deterministic id.

        Args:
            lemma_id: The deterministic id derived from ``(text, language)``.

        Returns:
            The matching lemma, or None when no lemma has the given id.
        """
