from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Optional, Tuple

# ---------- Preflight ----------

class PreflightPage(BaseModel):
    model_config = ConfigDict(extra='forbid')
    w_px: int = Field(ge=1)
    h_px: int = Field(ge=1)

class PreflightIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    standard: Literal['GOST', 'ISO', 'ASME', 'unknown']
    projection: Literal['first', 'third', 'unknown']
    units: Literal['mm', 'in']
    scale: str = Field(pattern=r'^\d+:\d+$')
    page: PreflightPage

class PreflightOut(PreflightIn):
    preflight_id: str
    normalized: dict

# ---------- Views ----------

class HolePx(BaseModel):
    model_config = ConfigDict(extra='forbid')
    center_px: Tuple[float, float]
    r_px: float = Field(ge=0)

class SolvedFlags(BaseModel):
    model_config = ConfigDict(extra='forbid')
    outer: bool
    holes: bool
    slots: Optional[bool] = None
    arcs: Optional[bool] = None

class Sketch(BaseModel):
    # Здесь допускаются дополнительные поля (по контракту)
    model_config = ConfigDict(extra='allow')
    outer_polygon_px: List[Tuple[float, float]]
    holes_px: List[HolePx] = Field(default_factory=list)
    slots_px: Optional[list] = None
    arcs_px: Optional[list] = None
    solved: SolvedFlags

class ViewItem(BaseModel):
    # Допускаем расширения
    model_config = ConfigDict(extra='allow')
    id: str
    bbox_px: Tuple[float, float, float, float]
    angle_deg: float
    sketch: Sketch

class ViewsIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    views: List[ViewItem]

class ViewsOut(BaseModel):
    views_count: int
    areas: dict               # id -> area
    solved_all: dict          # {'outer': bool, 'holes': bool, 'slots': bool, 'arcs': bool}
    stats: dict

# ---------- Plan ----------

class PlanIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    order: List[str]
    units: Literal['mm', 'in']
    notes: Optional[str] = None

class PlanOut(PlanIn):
    plan_id: str

# ---------- Features / Build ----------

class FeatureItem(BaseModel):
    # Разрешаем extra, т.к. фичи гибкие
    model_config = ConfigDict(extra='allow')
    type: str
    mode: Optional[Literal['extrude','revolve','cut_extrude','cut_revolve','add_extrude','add_revolve']] = None
    profile: Optional[str] = None
    thickness_mm: Optional[float] = None
    sketch: Optional[str] = None
    region: Optional[str] = None
    depth_mm: Optional[float] = None
    pos_mm: Optional[tuple] = None
    diam_mm: Optional[float] = None
    style: Optional[str] = None
    count: Optional[int] = None
    step_mm: Optional[float] = None
    pattern: Optional[Literal['linear','polar']] = None
    ref: Optional[str] = None
    thickness_shell_mm: Optional[float] = None
    d_mm: Optional[float] = None
    angle_deg: Optional[float] = None
    r_mm: Optional[float] = None

class BuildIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    features: List[FeatureItem]

class BuildOut(BaseModel):
    build_id: str
    features_count: int
    types_histogram: dict
    notes: Optional[str] = None

# ---------- Sketch2D ----------

class Sketch2DIn(BaseModel):
    model_config = ConfigDict(extra='allow')
    sketch: Sketch

class Sketch2DOut(BaseModel):
    sketch_id: str
    bbox_px: Tuple[float, float, float, float]
