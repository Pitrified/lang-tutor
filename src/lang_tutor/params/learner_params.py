"""Learner params for lang-tutor.

Who the tutor is teaching: the language being learned and the languages the
learner already knows. The known languages decide which look-alikes a word card
carries (`lang_tools.lexicon.LemmaCard.lookalikes`): a pt word that resembles an
en or it word is flagged as a trap (a false friend) or as free vocabulary (a
cognate). There are no per-user settings yet, so this is one process-wide
learner profile.

Environment variables:
    LANG_TUTOR_TARGET_LANGUAGE: ISO 639-1 code being learned. Defaults to ``pt``.
    LANG_TUTOR_KNOWN_LANGUAGES: comma-separated ISO 639-1 codes the learner
        knows. Defaults to ``en,it``.
"""

from __future__ import annotations

import os

from loguru import logger as lg

_DEFAULT_TARGET = "pt"
_DEFAULT_KNOWN = "en,it"


class LearnerParams:
    """Learner profile parameters loaded from environment variables."""

    def __init__(self) -> None:
        """Load the learner params from the environment."""
        lg.info("Loading LearnerParams")
        self._load_params()

    def _load_params(self) -> None:
        """Read the target and known languages from the environment."""
        self.target_language: str = (
            os.getenv("LANG_TUTOR_TARGET_LANGUAGE", _DEFAULT_TARGET).strip().lower()
        )
        known = os.getenv("LANG_TUTOR_KNOWN_LANGUAGES", _DEFAULT_KNOWN)
        self.known_languages: list[str] = [
            code
            for code in (part.strip().lower() for part in known.split(","))
            if code and code != self.target_language
        ]

    def __str__(self) -> str:
        """Return the string representation of the object."""
        s = "LearnerParams:"
        s += f"\n  target_language: {self.target_language}"
        s += f"\n  known_languages: {', '.join(self.known_languages)}"
        return s
