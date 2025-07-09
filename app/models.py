from pydantic import BaseModel
from typing import Optional
from enum import Enum

# the str correspond to the measurement name for influxdb query
class FeatEnum(str, Enum):
    step_time = "step_time"
    stand_time = "stand_time"
    sed_time = "sed_time"
    upr_time = "upr_time"
    step_cnt = "stepcount"

# Query Type
class WindowTimeFeatureQuery(BaseModel):
    userID: str
    window: str = "1h"
    now: str | None = None  # Optional override for "current time"
    fType: FeatEnum = FeatEnum.step_time

class DailyFeatureQuery(BaseModel):
    userID: str
    now: str | None = None

# Response Type
class WindowTimeFeatureResponse(BaseModel):
    userID: str
    window: str
    reference_time: str
    mean: float

class DailyFeatureResponse(BaseModel):
    userID: str
    reference_time: str
    value: Optional[float] = None   # allow None if not found
    found: bool = True              # indicator


class DemographicResponse(BaseModel):
    user_id: str
    dob: Optional[str]
    sex: Optional[int]
    ethnicity: Optional[dict]  # or make this a nested model if you want
    married: Optional[int]
    livealone: Optional[int]
    edu: Optional[int]
    prevExperi: Optional[int]
    BMI: Optional[float]
    total_days: Optional[int]
    age_enrolled: Optional[int]

# TODO: deviations based feature