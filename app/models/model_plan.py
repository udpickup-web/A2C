from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Optional


class ModelPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order: List[str] = Field(min_length=1)
    units: Literal["mm", "in"]
    notes: Optional[str] = None
