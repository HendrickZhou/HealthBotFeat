import logging
from influxdb_client import InfluxDBClient
from typing import List
from models import WindowTimeFeatureQuery, WindowTimeFeatureResponse
import os
from datetime import datetime, timedelta
import dateutil.parser

# Setup logging
logger = logging.getLogger(__name__)

# InfluxDB setup
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "mytoken")
INFLUX_ORG = os.getenv("INFLUX_ORG", "MyOrg")
INFLUX_BUCKET = "health_data"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

"""
    from(bucket: "health_data")
      |> range(start: 0)
      |> filter(fn: (r) =>
          r._measurement == "sed_time" and
          r.userID == "101"
      )
      |> group()
      |> mean()
"""
# Util
def parse_duration(s: str) -> timedelta:
    # basic parser for "1h", "24h", "7d"
    if s.endswith("h"):
        return timedelta(hours=int(s[:-1]))
    if s.endswith("d"):
        return timedelta(days=int(s[:-1]))
    raise ValueError("Unsupported window format. Use '1h', '24h', '7d', etc.")

def query_window_data(query: WindowTimeFeatureQuery) -> WindowTimeFeatureResponse:
    now = dateutil.parser.isoparse(query.now) if query.now else datetime.utcnow()
    duration = parse_duration(query.window)

    # be careful this is the only format that would work
    start = (now - duration).replace(tzinfo=None).isoformat() + "Z"
    stop = now.replace(tzinfo=None).isoformat() + "Z"

    flux = f'''
    from(bucket: "{os.getenv("INFLUX_BUCKET")}")
      |> range(start: {start}, stop: {stop})
      |> filter(fn: (r) =>
          r._measurement == "{query.fType.value}" and
          r.userID == "{query.userID}"
      )
      |> group()
      |> mean()
    '''

    logger.info(f"Running windowed query for userID={query.userID}, window={query.window}, now={stop}")
    logger.info(f"running flux script:{flux}")
    result = query_api.query(flux)

    # import pdb; pdb.set_trace()
    logger.info(f"query result: {result}")
    for table in result:
        for record in table.records:
            return WindowTimeFeatureResponse(
                userID=query.userID,
                window=query.window,
                reference_time=stop,
                mean_time=record.get_value()
            )
    return WindowTimeFeatureResponse(
        userID=query.userID,
        window=query.window,
        reference_time=stop,
        mean_time=0.0
    )