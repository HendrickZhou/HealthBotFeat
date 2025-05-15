from pydantic import BaseModel

class StepTimeFeatureQuery(BaseModel):
    userID: str
    window: str = "1h"
    now: str | None = None  # Optional override for "current time"

class StepTimeFeatureResponse(BaseModel):
    userID: str
    window: str
    reference_time: str
    mean_steptime: float
