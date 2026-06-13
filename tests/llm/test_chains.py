"""Tests for `lang_tutor.llm` chain factories.

These only verify that the in-package prompt matches the input model fields
(the eager validation in `StructuredLLMChain.__post_init__`). No real API
calls are made.
"""

from llm_core.chat.config.openai import ChatOpenAIConfig
from pydantic import SecretStr

from lang_tutor.llm import build_tutor_chain


def _cfg() -> ChatOpenAIConfig:
    return ChatOpenAIConfig(api_key=SecretStr("dummy"))


def test_build_tutor_chain() -> None:
    build_tutor_chain(_cfg())
