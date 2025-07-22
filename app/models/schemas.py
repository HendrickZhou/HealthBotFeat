from pydantic import BaseModel
from typing import Optional
from enum import Enum

# the str correspond to the measurement name for influxdb query
class PAEnum(str, Enum):
    step_time = "step_time"
    stand_time = "stand_time"
    sed_time = "sed_time"
    upr_time = "upr_time"
    step_cnt = "stepcount"

class EMAEnum(str, Enum):
    calm = "calm"
    tired = "tired"
    lonely = "lonely"
    pain = "pain"
    control = "control"
    feel = "feel"
    wherenow = "where_now"
    whowithnow = "whowith_now"
    naffect = "negative_affect"
    hrp = "high_arousal_pos"
    pcog = "per_cog"
    mindfulness = "mindfulness"

# general type
class MeanPASummary(BaseModel):
    steptime: float
    sedtime: float
    standtime: float
    uprtime: float
    stepcount: float

class EMASummary(BaseModel):
    calm: float
    tired: float
    lonely: float
    pain: float
    control: float
    feel: float
    wherenow: float
    whowithnow: float
    naffect : float
    hrp : float
    pcog : float
    mindfulness : float

# Query Type
class AggwrapFeatureQuery(BaseModel):
    userID: str
    now: str | None = None
    lastn: int

class WindowTimeFeatureQuery(BaseModel):
    """
    get result based on a time window 
    """
    userID: str
    window: str = "1h"
    now: str | None = None  # Optional override for "current time"
    fType: PAEnum = PAEnum.step_time

class DailyFeatureQuery(BaseModel):
    """
    get daily update type of result
    """
    userID: str
    now: str | None = None

class TimesBasedEMAQuery(BaseModel):
    """
    get result based on the last n times
    """
    userID: str
    type: EMAEnum
    lastn: int = 1
    now: str | None = None

# Response Type
class AggwrapFeatureResponse(BaseModel):
    userID: str
    timestamp: str
    last15: MeanPASummary
    last1h: MeanPASummary
    next15: MeanPASummary
    next1h: MeanPASummary
    ema: EMASummary

class WindowTimeFeatureResponse(BaseModel):
    userID: str
    window: str
    reference_time: str
    mean: float

class TimesBasedResponse(BaseModel):
    userID: str
    value: float
    timestamp: str

class DailyFeatureResponse(BaseModel):
    userID: str
    reference_time: str
    value: Optional[float] = None   # allow None if not found
    found: bool = True              # indicator

class DemographicResponse(BaseModel):
    userID: str
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