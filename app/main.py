import logging_config 
from fastapi import FastAPI, Query
from typing import List
from models import FeatEnum, WindowTimeFeatureQuery, WindowTimeFeatureResponse
from query import query_window_data

app = FastAPI(debug=True)

@app.get("/features/steptime", response_model=WindowTimeFeatureResponse)
def get_steptime_feature(userID: str, window: str = "1h", now: str | None = None):
    return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=FeatEnum.step_time))


@app.get("/features/sedtime", response_model=WindowTimeFeatureResponse)
def get_steptime_feature(userID: str, window: str = "1h", now: str | None = None):
    return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=FeatEnum.sed_time))


@app.get("/features/standtime", response_model=WindowTimeFeatureResponse)
def get_steptime_feature(userID: str, window: str = "1h", now: str | None = None):
    return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=FeatEnum.stand_time))


@app.get("/features/uprtime", response_model=WindowTimeFeatureResponse)
def get_steptime_feature(userID: str, window: str = "1h", now: str | None = None):
    return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=FeatEnum.upr_time))
