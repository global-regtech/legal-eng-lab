from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from legal_eng_lab.models import Provision, SourceDoc

GOOD_HASH = "a" * 64


def test_valid_provision_is_accepted() -> None:
    p = Provision(article=5, paragraph=1, point="a")
    assert p.model_dump() == {"article": 5, "paragraph": 1, "point": "a"}


@pytest.mark.parametrize(
    ("data", "error_type"),
    [
        pytest.param({"article": "5"}, "int_type", id="strict-no-string-to-int"),
        pytest.param({"article": 0}, "greater_than_equal", id="article-below-1"),
        pytest.param({"article": 5, "point": "z"}, "literal_error", id="unknown-point"),
        pytest.param({"article": 5, "confidence": 0.9}, "extra_forbidden", id="invented-field"),
        pytest.param({}, "missing", id="article-required"),
    ],
)
def test_bad_provision_is_rejected(data: dict[str, Any], error_type: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        Provision.model_validate(data)
    assert exc_info.value.errors()[0]["type"] == error_type


def test_provision_is_frozen() -> None:
    p = Provision(article=5)
    with pytest.raises(ValidationError, match="frozen"):
        p.article = 6


def test_json_round_trip() -> None:
    p = Provision(article=5, paragraph=1, point="f")
    assert Provision.model_validate_json(p.model_dump_json()) == p


def test_strict_date_python_vs_json() -> None:
    # Strict mode rejects a Python string for a date...
    with pytest.raises(ValidationError):
        SourceDoc.model_validate(
            {"eli": "eli/reg/2016/679/oj", "version_date": "2016-05-04", "sha256": GOOD_HASH}
        )
    # ...but JSON has no date type, so strict JSON validation accepts ISO date strings.
    doc = SourceDoc.model_validate_json(
        '{"eli": "eli/reg/2016/679/oj", "version_date": "2016-05-04", "sha256": "'
        + GOOD_HASH
        + '"}'
    )
    assert doc.version_date == date(2016, 5, 4)


def test_bad_hash_is_rejected() -> None:
    with pytest.raises(ValidationError, match="string_pattern_mismatch"):
        SourceDoc(eli="eli/reg/2016/679/oj", version_date=date(2016, 5, 4), sha256="ABC")
