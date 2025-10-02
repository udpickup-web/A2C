from pydantic import BaseModel, ConfigDict, conlist
from typing import List, Optional, Literal


class FeatureItem(BaseModel):
    model_config = ConfigDict(extra="allow")  # schemas allow extra on items
    type: str
    mode: Optional[
        Literal["extrude", "revolve", "cut_extrude", "cut_revolve", "add_extrude", "add_revolve"]
    ] = None
    profile: Optional[str] = None
    thickness_mm: Optional[float] = None
    sketch: Optional[str] = None
    region: Optional[str] = None
    depth_mm: Optional[float] = None
    pos_mm: Optional[conlist(float, min_length=2, max_length=3)] = None
    diam_mm: Optional[float] = None
    style: Optional[str] = None
    count: Optional[int] = None
    step_mm: Optional[float] = None
    pattern: Optional[Literal["linear", "polar"]] = None
    ref: Optional[str] = None
    thickness_shell_mm: Optional[float] = None
    d_mm: Optional[float] = None
    angle_deg: Optional[float] = None
    r_mm: Optional[float] = None


class Features(BaseModel):
    model_config = ConfigDict(extra="forbid")
    features: List[FeatureItem]
