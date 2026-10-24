"""LLM service layer for the interactive tutor.

The tutor response chain is the one interactive-feedback chain that lives in
`lang-tutor`. The content-producing chains (translation, conversation,
splitter, lemma_generator, topics, greeting) stay in `lang-tools`.

Public API:
    TutorInput, TutorOutput, CorrectionBlock, ConversationBlock, ErrorDetail,
        build_tutor_chain
"""

from lang_tutor.llm.tutor import ConversationBlock
from lang_tutor.llm.tutor import CorrectionBlock
from lang_tutor.llm.tutor import ErrorDetail
from lang_tutor.llm.tutor import TutorInput
from lang_tutor.llm.tutor import TutorOutput
from lang_tutor.llm.tutor import build_tutor_chain

__all__ = [
    "ConversationBlock",
    "CorrectionBlock",
    "ErrorDetail",
    "TutorInput",
    "TutorOutput",
    "build_tutor_chain",
]
