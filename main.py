# main.py
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import plotly.graph_objs as go
import time
import uvicorn
from utils.storage import *
from utils.db import DatabaseManager
from utils.plots import *
import asyncio
import ctypes
from utils.shared_state import SharedState
from collections import deque 
import random
import os 
from pydantic import BaseModel
from utils.collector import collect_data
from utils.calc_stats import *
import time
# import csv


class DataForm(BaseModel):
    num_samples: int
    data_type: str
    save_dir: str




app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/")
async def data_collection(request: Request):
    return templates.TemplateResponse("data_collection.html", {"request": request})


@app.post("/start-collection")
async def start_collection(form_data: DataForm):
    num_samples = form_data.num_samples
    data_type = form_data.data_type
    save_dir = form_data.save_dir

    s = time.time()
    file_path = collect_data(num_samples, data_type, save_dir)
    print(time.time() - s, "s collected")
    file_name = file_path.split("/")[-1]
    dir_size = get_dir_size(save_dir)
    avlb_storage = get_available_disk_space(save_dir)

    if num_samples != 1: 
        stats = calc_signal_stats_avg(file_path)
    else:
        stats = calc_signal_stats(file_path)
    result = {
        "status": "success",
        "message": "data collected",
        "file_name": file_name,
        "data_type": data_type,
        "save_dir": save_dir,
        "dir_size": dir_size,
        "avlb_storage": avlb_storage,
        "stats": stats
    }

    return result


async def main():
    config = config = uvicorn.Config(app, host="localhost", port=8000, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()
   
if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Server stopped by user with Ctrl + C")