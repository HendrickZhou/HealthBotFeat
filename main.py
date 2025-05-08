# Feature Platform: FastAPI + InfluxDB + Redis-ready + gRPC-extensible

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from influxdb import InfluxDBClient
import os
import redis

app = FastAPI(title="Feature Platform", description="InfluxDB + FastAPI + Redis-ready")

# ----- InfluxDB Setup ----- #
INFLUX_HOST = os.getenv("INFLUX_HOST", "localhost")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", 8086))
INFLUX_DB = os.getenv("INFLUX_DB", "health")

influx = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
influx.switch_database(INFLUX_DB)

# ----- Redis (optional, for caching) ----- #
USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"
if USE_REDIS:
    redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)

# ----- Pydantic Response Schema ----- #
class FeatureResponse(BaseModel):
    user_id: str
    avg_hr_1d: float | None = None
    steps_7d: int | None = None

# ----- Query Logic (with optional Redis caching) ----- #
def query_avg_heart_rate(user_id: str) -> float | None:
    q = f"""
        SELECT MEAN(heart_rate) FROM health_metrics
        WHERE user_id = '{user_id}' AND time > now() - 1d
    """
    res = influx.query(q)
    points = list(res.get_points())
    return points[0]['mean'] if points else None

def query_steps_7d(user_id: str) -> int | None:
    q = f"""
        SELECT SUM(steps) FROM health_metrics
        WHERE user_id = '{user_id}' AND time > now() - 7d
    """
    res = influx.query(q)
    points = list(res.get_points())
    return int(points[0]['sum']) if points else None

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

# ----- TODO: gRPC Extensibility ----- #
# This module is structured so you can plug in gRPC interface later
# Simply abstract the query functions into a service class, and call from both FastAPI and gRPC

