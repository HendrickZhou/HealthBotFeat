from fastapi import APIRouter
from models.schemas import *
from services.query_influx import query_window_data, query_sq_data, query_ema_lastn
from services.query_mongo import query_demographics
from http.client import HTTPException
from typing import List

"""
/ema?type=calm
/pa?type=steptime

/agg?
"""


router = APIRouter()

# @router.get("/steptime", response_model=WindowTimeFeatureResponse)
# def get_steptime_feature(userID: str, window: str = "1h", now: str | None = None):
#     return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=PAEnum.step_time))

# @router.get("/sedtime", response_model=WindowTimeFeatureResponse)
# def get_sedtime_feature(userID: str, window: str = "1h", now: str | None = None):
#     return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=PAEnum.sed_time))

# @router.get("/standtime", response_model=WindowTimeFeatureResponse)
# def get_standtime_feature(userID: str, window: str = "1h", now: str | None = None):
#     return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=PAEnum.stand_time))

# @router.get("/uprtime", response_model=WindowTimeFeatureResponse)
# def get_uprtime_feature(userID: str, window: str = "1h", now: str | None = None):
#     return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=PAEnum.upr_time))

# @router.get("/stepcount", response_model=WindowTimeFeatureResponse)
# def get_stepcnt_feature(userID: str, window: str = "1h", now: str | None = None):
#     return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=PAEnum.step_cnt))

# TODO probabliy seperate the Eum definition here
@router.get("/pa", response_model=WindowTimeFeatureResponse)
def get_pa_feature(userID: str, type: PAEnum, window: str = "1h", now: str | None = None):
    return query_window_data(WindowTimeFeatureQuery(userID=userID, window=window, now=now, fType=type))

# We're simplifying the feature of sq, the sleep time cutoff is at 2:00AM
@router.get("/sq", response_model=DailyFeatureResponse)
def get_sq_feature(userID: str, now: str | None = None):
    return query_sq_data(DailyFeatureQuery(userID=userID, now=now))

@router.get("/demographics", response_model=DemographicResponse)
def get_demographics(user_id: str):
    data = query_demographics(user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data

@router.get("/ema", response_model=List[TimesBasedResponse])
def get_ema(userID: str, type: EMAEnum, lastn: int = 1, now: str | None = None):
    return query_ema_lastn(TimesBasedEMAQuery(userID=userID, type=type, lastn=lastn, now=now))