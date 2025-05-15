from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import redis

app = FastAPI(title="Feature Platform", description="InfluxDB 2.0 + FastAPI + Redis-ready")

# ----- InfluxDB 2.0 Setup ----- #
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "mytoken")
INFLUX_ORG = os.getenv("INFLUX_ORG", "MyOrg")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "health_data")

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = influx_client.query_api()

# ----- Redis (optional, for caching) ----- #
USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"
if USE_REDIS:
    redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)

# ----- Pydantic Response Schema ----- #
class FeatureResponse(BaseModel):
    user_id: str
    avg_hr_1d: float | None = None
    steps_7d: int | None = None

# ----- Query Logic (with Flux) ----- #
def query_avg_heart_rate(user_id: str) -> float | None:
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -1d)
      |> filter(fn: (r) => r["_measurement"] == "health_metrics")
      |> filter(fn: (r) => r["user_id"] == "{user_id}")
      |> filter(fn: (r) => r["_field"] == "heart_rate")
      |> mean()
    '''
    tables = query_api.query(query)
    for table in tables:
        for record in table.records:
            return float(record.get_value())
    return None

def query_steps_7d(user_id: str) -> int | None:
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -7d)
      |> filter(fn: (r) => r["_measurement"] == "health_metrics")
      |> filter(fn: (r) => r["user_id"] == "{user_id}")
      |> filter(fn: (r) => r["_field"] == "steps")
      |> sum()
    '''
    tables = query_api.query(query)
    for table in tables:
        for record in table.records:
            return int(record.get_value())
    return None

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

