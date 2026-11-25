import pytest

import legal_eng_lab

ART_33_Opening = "In the case of personal data breach, the controller shall without undue delay"


@pytest.fixture
def art_33_text() -> str:
    """Shared text input that pytest hands over to any test that asks it by name"""
    return ART_33_Opening


def test_package_imports() -> None:
    assert legal_eng_lab.__name__ == "legal_eng_lab"


def test_fixture_is_injected(art_33_text: str) -> None:
    assert art_33_text.startswith("In the case of")


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("controller", True),
        ("processor", False),
        ("72 hours", False),
    ],
)
def test_word_in_opening(art_33_text: str, word: str, expected: bool) -> None:
    assert (word in art_33_text) is expected
