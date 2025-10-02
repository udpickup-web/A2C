from pydantic import BaseModel, Field, ConfigDict, conlist
from typing import List, Tuple

Point = conlist(float, min_length=2, max_length=2)
BBox = conlist(float, min_length=4, max_length=4)

class Solved(BaseModel):
    model_config = ConfigDict(extra="forbid")
    outer: bool
    holes: bool
    slots: bool | None = None
    arcs: bool | None = None

class Hole(BaseModel):
    model_config = ConfigDict(extra="forbid")
    center_px: Point
    r_px: float = Field(ge=0)

class Sketch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    outer_polygon_px: List[Point] = Field(min_length=3)
    holes_px: List[Hole] = Field(default_factory=list)
    slots_px: list = Field(default_factory=list)
    arcs_px: list = Field(default_factory=list)
    solved: Solved

class ViewItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    bbox_px: BBox
    angle_deg: float
    sketch: Sketch

class Views(BaseModel):
    model_config = ConfigDict(extra="forbid")
    views: List[ViewItem]
