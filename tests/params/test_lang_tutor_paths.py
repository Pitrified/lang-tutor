"""Test the lang_tutor paths."""

from lang_tutor.params.lang_tutor_params import get_lang_tutor_paths


def test_lang_tutor_paths() -> None:
    """Test the lang_tutor paths."""
    lang_tutor_paths = get_lang_tutor_paths()
    assert lang_tutor_paths.src_fol.name == "lang_tutor"
    assert lang_tutor_paths.root_fol.name == "lang-tutor"
    assert lang_tutor_paths.data_fol.name == "data"
