import logging_config 
from fastapi import FastAPI, Query
from typing import List
from models import *
from query_influx import query_window_data, query_sq_data
from query_mongo import query_demographics
from http.client import HTTPException

app = FastAPI(debug=True)

@app.get("/features/steptime", response_model=WindowTimeFeatureResponse)
def get_steptime_feature(userID: str, window: str = "1h", now: str | None = None):
    return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=FeatEnum.step_time))


@app.get("/features/sedtime", response_model=WindowTimeFeatureResponse)
def get_sedtime_feature(userID: str, window: str = "1h", now: str | None = None):
    return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=FeatEnum.sed_time))

@app.get("/features/standtime", response_model=WindowTimeFeatureResponse)
def get_standtime_feature(userID: str, window: str = "1h", now: str | None = None):
    return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=FeatEnum.stand_time))

@app.get("/features/uprtime", response_model=WindowTimeFeatureResponse)
def get_uprtime_feature(userID: str, window: str = "1h", now: str | None = None):
    return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=FeatEnum.upr_time))

# We're simplifying the feature of sq, the sleep time cutoff is at 2:00AM
@app.get("/features/sq", response_model=DailyFeatureResponse)
def get_sq_feature(userID: str, now: str | None = None):
    return query_sq_data(DailyFeatureQuery(userID=userID, now=now))


@app.get("/demographics", response_model=DemographicResponse)
def get_demographics(user_id: str):
    data = query_demographics(user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data