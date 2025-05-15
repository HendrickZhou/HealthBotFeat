from pydantic import BaseModel
from typing import List

class StepTimeQuery(BaseModel):
    userID: str
    start: str = "1970-01-01T00:00:00Z"
    stop: str = "now()"

class StepTimeRecord(BaseModel):
    steptime: float

