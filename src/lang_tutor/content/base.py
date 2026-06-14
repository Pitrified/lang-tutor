"""Content source interface.

`ContentSource` is the single seam through which `lang-tutor` reads word
content. It mirrors the frozen `lang_tools.words.word_store` read helpers so
the in-process and HTTP implementations are drop-in interchangeable; switching
transport is a one-line change in the factory, not a change at every call site.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lang_tools.words.word import Word


class ContentSource(ABC):
    """Read-only access to the `lang-tools` word content.

    Implementations differ only in transport: an in-process read of the word
    store or an HTTP call to the `lang-tools` read service. Both return the same
    `Word` model, so callers are unaware of which one is wired in.
    """

    @abstractmethod
    def get_words_filtered(
        self,
        language: str | None = None,
        topic: str | None = None,
    ) -> list[Word]:
        """Return words filtered by optional language and/or topic.

        Args:
            language: ISO 639-1 code to filter by. No filter when None.
            topic: Topic tag to filter by. No filter when None.

        Returns:
            The matching words (the full pool when no filter is given).
        """

    @abstractmethod
    def get_word_by_id(self, word_id: str) -> Word | None:
        """Return a single word by its deterministic id.

        Args:
            word_id: The deterministic id derived from ``(text, language)``.

        Returns:
            The matching word, or None when no word has the given id.
        """
