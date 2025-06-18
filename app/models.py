from pydantic import BaseModel
from enum import Enum

class FeatEnum(str, Enum):
    step_time = "step_time"
    stand_time = "stand_time"
    sed_time = "sed_time"
    upr_time = "upr_time"

class WindowTimeFeatureQuery(BaseModel):
    userID: str
    window: str = "1h"
    now: str | None = None  # Optional override for "current time"
    fType: FeatEnum = FeatEnum.step_time

class WindowTimeFeatureResponse(BaseModel):
    userID: str
    window: str
    reference_time: str
    mean_time: float
