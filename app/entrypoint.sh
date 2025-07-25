#!/bin/bash

if [ "$ENV" = "dev" ]; then
    exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
else
    exec uvicorn main:app --host 0.0.0.0 --port 8000
fi
