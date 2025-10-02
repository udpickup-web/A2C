from pydantic import BaseModel, Field, ConfigDict, constr
from typing import Literal


class Page(BaseModel):
    model_config = ConfigDict(extra="forbid")
    w_px: int = Field(ge=1)
    h_px: int = Field(ge=1)


class Preflight(BaseModel):
    model_config = ConfigDict(extra="forbid")
    standard: Literal["GOST", "ISO", "ASME", "unknown"]
    projection: Literal["first", "third", "unknown"]
    units: Literal["mm", "in"]
    scale: constr(pattern=r"^\d+:\d+$")
    page: Page
