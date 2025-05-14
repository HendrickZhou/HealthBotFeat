from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from influxdb_client_3 import InfluxDBClient3
import os
import redis
import pandas as pd

app = FastAPI(title="Feature Platform", description="InfluxDB 3.0 + FastAPI + Redis-ready")

# ----- InfluxDB 3.0 Setup ----- #
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")  # Optional, can be left blank for OSS
INFLUX_DATABASE = os.getenv("INFLUX_DATABASE")  # Replace with bucket name

client = InfluxDBClient3(
    token=INFLUX_TOKEN,
    host=INFLUX_URL,
    database=INFLUX_DATABASE
)

# ----- Redis (optional, for caching) ----- #
USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"
if USE_REDIS:
    redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)

# ----- Pydantic Response Schema ----- #
class FeatureResponse(BaseModel):
    user_id: str
    avg_hr_1d: float | None = None
    steps_7d: int | None = None

# ----- Query Logic (with InfluxDB 3.0 SQL) ----- #
def query_avg_heart_rate(user_id: str) -> float | None:
    sql = f"""
        SELECT MEAN(heart_rate) AS mean_hr
        FROM health_metrics
        WHERE time > now() - interval '1 day' AND user_id = '{user_id}'
    """
    df: pd.DataFrame = client.query(query=sql)
    return float(df["mean_hr"].iloc[0]) if not df.empty else None

def query_steps_7d(user_id: str) -> int | None:
    sql = f"""
        SELECT SUM(steps) AS total_steps
        FROM health_metrics
        WHERE time > now() - interval '7 days' AND user_id = '{user_id}'
    """
    df: pd.DataFrame = client.query(query=sql)
    return int(df["total_steps"].iloc[0]) if not df.empty else None

# ----- FastAPI Endpoint ----- #
@app.get("/features", response_model=FeatureResponse)
def get_features(user_id: str):
    cache_key = f"features:{user_id}"

    if USE_REDIS and redis_client.exists(cache_key):
        return FeatureResponse(**eval(redis_client.get(cache_key)))

    avg_hr = query_avg_heart_rate(user_id)
    steps = query_steps_7d(user_id)

    if avg_hr is None and steps is None:
        raise HTTPException(status_code=404, detail="No data found")

    result = FeatureResponse(user_id=user_id, avg_hr_1d=avg_hr, steps_7d=steps)

    if USE_REDIS:
        redis_client.setex(cache_key, 60, str(result.dict()))

    return result

