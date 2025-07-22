import logging
from influxdb_client import InfluxDBClient
from config.setting import settings
from typing import List
from models.schemas import *
import os
from datetime import datetime, timedelta
import dateutil.parser

# Setup logging
logger = logging.getLogger(__name__)

# InfluxDB setup
INFLUX_BUCKET = settings.influx_bucket

client = InfluxDBClient(
    url=settings.influx_url,
    token=settings.influx_token,
    org=settings.influx_org,
)
query_api = client.query_api()

# Util
def parse_duration(s: str) -> timedelta:
    # basic parser for "1h", "24h", "7d"
    if s.endswith("h"):
        return timedelta(hours=int(s[:-1]))
    if s.endswith("d"):
        return timedelta(days=int(s[:-1]))
    raise ValueError("Unsupported window format. Use '1h', '24h', '7d', etc.")

def parse_now(now_str: str | None) -> datetime:
    return dateutil.parser.isoparse(now_str) if now_str else datetime.now(datetime.timezone.utc)



######################
# def get_aggregated_data(query: AggwrapFeatureQuery) -> List[]:
    """
    get the aggregated data
    for each report of ema, get three levels of mean activity report: 15mins/1hour TODO: more resultion?
    we should return structured result 
    """
    # query_window_data(WindowTimeFeatureQuery(userID=query.userID, ))
    pass

def get_deviation():
    """
    get the deviation from averages
    """
    pass


######################
def query_ema_lastn(query: TimesBasedEMAQuery) -> List[TimesBasedResponse]:
    now = parse_now(query.now)
    stop = now.replace(tzinfo=None).isoformat() + "Z"

    flux = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: 0, stop: {stop})  // use a large enough window
      |> filter(fn: (r) =>
          r._measurement == "{query.type.value}" and
          r.userID == "{query.userID}"
      )
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: {query.lastn})
    '''
    logger.info(f"Running EMA lastn query for userID={query.userID}, type={query.type}, lastn={query.lastn}, now={stop}")
    logger.info(f"running flux script: {flux}")
    result = query_api.query(flux)

    responses = []
    for table in result:
        for record in table.records:
            responses.append(TimesBasedResponse(
                userID=query.userID,
                value=record.get_value(),
                timestamp=record.get_time().isoformat()
            ))
    return responses

def query_window_data(query: WindowTimeFeatureQuery) -> WindowTimeFeatureResponse:
    now = parse_now(query.now)
    duration = parse_duration(query.window)

    # be careful this is the only format that would work
    start = (now - duration).replace(tzinfo=None).isoformat() + "Z"
    stop = now.replace(tzinfo=None).isoformat() + "Z"

    flux = f'''
    from(bucket: "{INFLUX_BUCKET}")
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
                mean=record.get_value()
            )
    return WindowTimeFeatureResponse(
        userID=query.userID,
        window=query.window,
        reference_time=stop,
        mean=0.0
    )

def query_sq_data(query: DailyFeatureQuery) -> DailyFeatureResponse:
    now = parse_now(query.now)

    # Apply 2 AM cutoff logic
    if now.hour < 2:
        sleep_day = (now - timedelta(days=1)).date()
    else:
        sleep_day = now.date()

    # Time range: from 00:00 of sleep_day to 00:00 of next day
    day_start = datetime.combine(sleep_day, datetime.min.time())
    day_end = day_start + timedelta(days=1)

    # Format time as: 2025-06-18T00:00:00Z
    start = day_start.replace(tzinfo=None).isoformat() + "Z"
    stop = day_end.replace(tzinfo=None).isoformat() + "Z"

    # Flux query
    flux = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {start}, stop: {stop})
      |> filter(fn: (r) =>
          r._measurement == "sleep_quality" and
          r.userID == "{query.userID}"
      )
      |> last()
    '''

    result = query_api.query(flux)

    for table in result:
        for record in table.records:
            return DailyFeatureResponse(
                userID=query.userID,
                reference_time=record.get_time().isoformat(),
                value=record.get_value(),
                found=True
            )

    return DailyFeatureResponse(
        userID=query.userID,
        reference_time=start,
        value=None,
        found=False
    )