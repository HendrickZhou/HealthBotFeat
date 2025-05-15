import logging_config 
from fastapi import FastAPI, Query
from typing import List
from models import StepTimeFeatureQuery, StepTimeFeatureResponse
from query import query_steptime_data

app = FastAPI()

@app.get("/features/steptime", response_model=StepTimeFeatureResponse)
def get_steptime_feature(userID: str, window: str = "1h", now: str | None = None):
    return query_steptime_data(StepTimeFeatureQuery(userID=userID, window=window, now=now))
