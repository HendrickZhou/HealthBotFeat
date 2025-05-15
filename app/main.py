import logging_config 
from fastapi import FastAPI, Query
from typing import List
from models import StepTimeQuery, StepTimeRecord
from query import query_steptime_data

app = FastAPI()
@app.get("/steptime", response_model=List[StepTimeRecord])
def get_steptime(query: StepTimeQuery = Query(...)):
    return query_steptime_data(query)

