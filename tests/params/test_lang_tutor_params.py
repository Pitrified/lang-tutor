"""Test the LangTutorParams class."""

from lang_tutor.params.lang_tutor_params import LangTutorParams
from lang_tutor.params.lang_tutor_params import get_lang_tutor_params
from lang_tutor.params.lang_tutor_paths import LangTutorPaths
from lang_tutor.params.sample_params import SampleParams


def test_lang_tutor_params_singleton() -> None:
    """Test that LangTutorParams is a singleton."""
    params1 = LangTutorParams()
    params2 = LangTutorParams()
    assert params1 is params2
    assert get_lang_tutor_params() is params1


def test_lang_tutor_params_init() -> None:
    """Test initialization of LangTutorParams."""
    params = LangTutorParams()
    assert isinstance(params.paths, LangTutorPaths)
    assert isinstance(params.sample, SampleParams)


def test_lang_tutor_params_str() -> None:
    """Test string representation."""
    params = LangTutorParams()
    s = str(params)
    assert "LangTutorParams:" in s
    assert "LangTutorPaths:" in s
    assert "SampleParams:" in s
