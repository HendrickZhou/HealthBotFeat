import logging
from influxdb_client import InfluxDBClient
from typing import List
from models import StepTimeQuery, StepTimeRecord
import os

# Setup logging
logger = logging.getLogger(__name__)

# InfluxDB setup
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "mytoken")
INFLUX_ORG = os.getenv("INFLUX_ORG", "MyOrg")
INFLUX_BUCKET = "health_data"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

def query_steptime_data(query: StepTimeQuery) -> List[StepTimeRecord]:
    flux = f'''
    from(bucket: "{os.getenv("INFLUX_BUCKET")}")
      |> range(start: {query.start}, stop: {query.stop})
      |> filter(fn: (r) =>
          r._measurement == "step_time" and
          r.userID == "{query.userID}" and
          r._field == "steptime"
      )
      |> group()
      |> mean()
    '''

    logger.info(f"Running InfluxDB query for userID={query.userID}, start={query.start}, stop={query.stop}")
    logger.info(f"Flux query: {flux}")

    try:
        result = query_api.query(flux)
        for table in result:
            for record in table.records:
                return [StepTimeRecord(
                    steptime=record.get_value()
                )]
        return []
    except Exception as e:
        logger.error(f"InfluxDB query failed: {e}")
        raise
