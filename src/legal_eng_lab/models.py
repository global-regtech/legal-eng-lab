"'First Pydantic models"

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

STRICT = ConfigDict(strict=True, extra="forbid", frozen=True)


class Provision(BaseModel):
    """A citable unit of a regulation, e.g. GDPR Art. 5(1)(a)."""

    model_config = STRICT

    article: int = Field(ge=1, le=99)
    paragraph: int | None = Field(default=None, ge=1)
    point: Literal["a", "b", "c", "d", "e", "f"] | None = None


class SourceDoc(BaseModel):
    """The exact text a record was taken from."""

    model_config = STRICT

    eli: str = Field(pattern=r"^eli/reg/\d{4}/\d+/oj$")
    version_date: date
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
