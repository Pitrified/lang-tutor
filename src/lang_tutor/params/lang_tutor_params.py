"""LangTutor project params.

Parameters are actual value of the config.

The class is a singleton, so it can be accessed from anywhere in the code.

There is a parameter regarding the environment type (stage and location), which
is used to load different paths and other parameters based on the environment.
"""

from loguru import logger as lg

from lang_tutor.metaclasses.singleton import Singleton
from lang_tutor.params.content_params import ContentParams
from lang_tutor.params.env_type import EnvType
from lang_tutor.params.lang_tutor_paths import LangTutorPaths
from lang_tutor.params.learner_params import LearnerParams
from lang_tutor.params.llm_params import LlmParams
from lang_tutor.params.sample_params import SampleParams
from lang_tutor.params.webapp import WebappParams


class LangTutorParams(metaclass=Singleton):
    """LangTutor project parameters."""

    def __init__(self) -> None:
        """Load the LangTutor params."""
        lg.info("Loading LangTutor params")
        self.set_env_type()

    def set_env_type(self, env_type: EnvType | None = None) -> None:
        """Set the environment type.

        Args:
            env_type (EnvType | None): The environment type.
                If None, it will be set from the environment variables.
                Defaults to None.
        """
        if env_type is not None:
            self.env_type = env_type
        else:
            self.env_type = EnvType.from_env_var()
        self.load_config()

    def load_config(self) -> None:
        """Load the lang_tutor configuration."""
        self.paths = LangTutorPaths(env_type=self.env_type)
        self.sample = SampleParams()
        self.llm = LlmParams()
        self.content = ContentParams()
        self.learner = LearnerParams()
        self.webapp = WebappParams(
            stage=self.env_type.stage,
            location=self.env_type.location,
        )

    def __str__(self) -> str:
        """Return the string representation of the object."""
        s = "LangTutorParams:"
        s += f"\n{self.paths}"
        s += f"\n{self.sample}"
        s += f"\n{self.llm}"
        s += f"\n{self.content}"
        s += f"\n{self.learner}"
        s += f"\n{self.webapp}"
        return s

    def __repr__(self) -> str:
        """Return the string representation of the object."""
        return str(self)


def get_lang_tutor_params() -> LangTutorParams:
    """Get the lang_tutor params."""
    return LangTutorParams()


def get_lang_tutor_paths() -> LangTutorPaths:
    """Get the lang_tutor paths."""
    return get_lang_tutor_params().paths


def get_webapp_params() -> WebappParams:
    """Get the webapp params."""
    return get_lang_tutor_params().webapp


def get_llm_params() -> LlmParams:
    """Get the LLM params."""
    return get_lang_tutor_params().llm


def get_content_params() -> ContentParams:
    """Get the content source params."""
    return get_lang_tutor_params().content


def get_learner_params() -> LearnerParams:
    """Get the learner params (target and known languages)."""
    return get_lang_tutor_params().learner
