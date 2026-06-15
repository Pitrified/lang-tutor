"""Content source interface.

`ContentSource` is the single seam through which `lang-tutor` reads lemma
content. It mirrors the frozen `lang_tools.lexicon.lemma_store` read helpers so
the in-process and HTTP implementations are drop-in interchangeable; switching
transport is a one-line change in the factory, not a change at every call site.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lang_tools.lexicon.lemma import Lemma


class ContentSource(ABC):
    """Read-only access to the `lang-tools` lemma content.

    Implementations differ only in transport: an in-process read of the lemma
    store or an HTTP call to the `lang-tools` read service. Both return the same
    `Lemma` model, so callers are unaware of which one is wired in.
    """

    @abstractmethod
    def get_lemmas_filtered(
        self,
        language: str | None = None,
        topic: str | None = None,
    ) -> list[Lemma]:
        """Return lemmas filtered by optional language and/or topic.

        Args:
            language: ISO 639-1 code to filter by. No filter when None.
            topic: Topic tag to filter by. No filter when None.

        Returns:
            The matching lemmas (the full pool when no filter is given).
        """

    @abstractmethod
    def get_lemma_by_id(self, lemma_id: str) -> Lemma | None:
        """Return a single lemma by its deterministic id.

        Args:
            lemma_id: The deterministic id derived from ``(text, language)``.

        Returns:
            The matching lemma, or None when no lemma has the given id.
        """
