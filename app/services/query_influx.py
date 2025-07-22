import logging
from influxdb_client import InfluxDBClient
from config.setting import settings
from typing import List, Tuple
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
    if s.endswith("m"):
        return timedelta(minutes=int(s[:-1]))
    raise ValueError("Unsupported window format. Use '5m', '1h', '24h', '7d', etc.")

def parse_now(now_str: str | None) -> datetime:
    return dateutil.parser.isoparse(now_str) if now_str else datetime.now(datetime.timezone.utc)

######################
def _query_window_mean(now: str, window: str, userID: str, type: PAEnum) -> Tuple[float, str]:
    now = parse_now(now)
    duration = parse_duration(window)

    # be careful this is the only format that would work
    start = (now - duration).replace(tzinfo=None).isoformat() + "Z"
    stop = now.replace(tzinfo=None).isoformat() + "Z"

    flux = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {start}, stop: {stop})
      |> filter(fn: (r) =>
          r._measurement == "{type.value}" and
          r.userID == "{userID}"
      )
      |> group()
      |> mean()
    '''

    # logger.info(f"Running windowed query for userID={userID}, window={window}, now={stop}")
    # logger.info(f"running flux script:{flux}")
    result = query_api.query(flux)
    if not result:
        logger.warning("NO data returned from query")
    # logger.info(f"query result: {result}")
    for table in result:
        for record in table.records:
            return (record.get_value(), stop)
    return (0.0, stop)

######################
def get_aggregated_data(query: AggwrapFeatureQuery) -> List[AggwrapFeatureResponse]:
    """
    get the aggregated data
    for each report of ema, get three levels of mean activity report: 15mins/1hour TODO: more resultion?
    we should return structured result 
    """
    now = parse_now(query.now)
    stop = now.replace(tzinfo=None).isoformat() + "Z"
    # Step 1: Query last N EMA records of all types
    flux = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: 0, stop: {stop})
      |> filter(fn: (r) => 
          r.userID == "{query.userID}" and
          r._measurement =~ /^({ '|'.join(e.value for e in EMAEnum) })$/
      )
      |> group(columns: ["userID"])
      |> pivot(rowKey:["_time"], columnKey: ["_measurement"], valueColumn: "_value")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: {query.lastn})
    '''
    logger.info(f"Running aggregated EMA+PA query for userID={query.userID}")
    logger.info(f"Flux: {flux}")
    result = query_api.query(flux)

    responses = []

    pa_metrics = {
        "steptime": PAEnum.step_time,
        "sedtime": PAEnum.sed_time,
        "standtime": PAEnum.stand_time,
        "uprtime": PAEnum.upr_time,
        "stepcount": PAEnum.step_cnt
    }

    def collect_pa_summary(ts: str, window: str) -> MeanPASummary:
        values = {}
        for key, pa_enum in pa_metrics.items():
            val, _ = _query_window_mean(now=ts, window=window, userID=query.userID, type=pa_enum)
            values[key] = val
        return MeanPASummary(**values)
    current_time = parse_now(query.now)

    logger.info(result)
    for table in result:
        for record in table.records:
            logger.info("!")

            timestamp = record.get_time()
            ts_str = timestamp.isoformat()

            # Past windows
            last15 = collect_pa_summary(ts_str, "15m")
            last1h = collect_pa_summary(ts_str, "1h")

            # Query future windows (add time before passing as "now")
            future_15 = timestamp + timedelta(minutes=15)
            future_1h = timestamp + timedelta(hours=1)

            if future_15 <= current_time:
                next15 = collect_pa_summary(future_15.isoformat(), "15m")
            else:
                next15 = MeanPASummary(**{k: 0.0 for k in pa_metrics})

            if future_1h <= current_time:
                next1h = collect_pa_summary(future_1h.isoformat(), "1h")
            else:
                next1h = MeanPASummary(**{k: 0.0 for k in pa_metrics})


            # Step 3: Build EMA summary from available fields
            ema_summary = EMASummary(
                calm=record.values.get("calm") or 0.0,
                tired=record.values.get("tired") or 0.0,
                lonely=record.values.get("lonely") or 0.0,
                pain=record.values.get("pain") or 0.0,
                control=record.values.get("control") or 0.0,
                feel=record.values.get("feel") or 0.0,
                wherenow=record.values.get("where_now") or 0.0,
                whowithnow=record.values.get("whowith_now") or 0.0,
                naffect=record.values.get("negative_affect") or 0.0,
                hrp=record.values.get("high_arousal_pos") or 0.0,
                pcog=record.values.get("per_cog") or 0.0,
                mindfulness=record.values.get("mindfulness") or 0.0
            )

            responses.append(AggwrapFeatureResponse(
                userID=query.userID,
                timestamp=ts_str,
                ema=ema_summary,
                last15=last15,
                last1h=last1h,
                next15=next15,
                next1h=next1h
            ))

    return responses
    

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
    mean, stop = _query_window_mean(query.now, query.window,query.userID,query.fType)
    return WindowTimeFeatureResponse(
        userID=query.userID,
        window=query.window,
        reference_time=stop,
        mean=mean
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