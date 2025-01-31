#!/usr/bin/env python3
import json
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from api import get_data
import asyncio

import signal
import threading
from datetime import datetime
from typing import Dict
import logging
from functools import partial

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class DataSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # This code ensures there is only a only a one instance of this class hence singleton
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.data = {}
                cls._instance.counter = 0
                cls._instance.last_update = None
            return cls._instance

    async def update_data(self):
        try:
            self.data = await get_data()
            print(self.data)
            self.last_update = datetime.now()
            logger.info("Data updated successfully")
        except Exception as e:
            logger.error(f"Failed to update data: {e}")

    def get_data(self) -> Dict:
        return self.data

app = FastAPI()
data_singleton = DataSingleton()

def signal_handler(signum, frame, loop):
    """Handle the update signal by scheduling the async update in the event loop"""
    logger.info(f"Received signal {signum}, scheduling data update...")

    async def update_wrapper():
        await data_singleton.update_data()

    asyncio.run_coroutine_threadsafe(update_wrapper(), loop)


@app.on_event("startup")
async def startup_event():
    # Initialize data on startup
    await data_singleton.update_data()
    logger.info("FastAPI application started, initial data loaded")

    # Get the current event loop and set up signal handler
    loop = asyncio.get_running_loop()
    signal.signal(signal.SIGUSR1, partial(signal_handler, loop=loop))

@app.get("/data")
async def get_data():
    return data_singleton.get_data()

@app.get("/last-update")
async def get_last_update():
    return {"last_update": data_singleton.last_update}

@app.get("/")
async def root():
    return FileResponse("public/index.html")
