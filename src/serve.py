#!/usr/bin/env python3
import json
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()


@app.get("/")
async def root():
    return FileResponse("src/public/index.html")


@app.get("/current_product.jpg")
async def get_image():
    return FileResponse("src/public/current_product.jpg")


@app.get("/current_values.json")
async def get_values():
    with open("src/public/current_values.json") as f:
        data = json.load(f)
    return JSONResponse(data)
