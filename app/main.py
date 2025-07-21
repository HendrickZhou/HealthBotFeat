import config.logging_config as logging_config 
from fastapi import FastAPI
from api.high_level.routes import router as high_level_router
from typing import List

app = FastAPI(debug=True)

app.include_router(high_level_router, prefix="/api/features", tags=["High-Level API"])