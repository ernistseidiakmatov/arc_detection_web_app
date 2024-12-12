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
    print(num_samples)
    print(data_type)
    print(save_dir)

    file_name = collect_data(num_samples, data_type, save_dir)
    dir_size = get_dir_size(save_dir)
    avlb_storage = get_available_disk_space(save_dir)

    result = {
        "status": "success",
        "message": "data collected",
        "file_name": file_name,
        "data_type": data_type,
        "save_dir": save_dir,
        "dir_size": dir_size,
        "avln_storage": avlb_storage
    }

    print(result)

    return result





# @app.post("/")
# async def handle_data_collection(request: Request, num_samples: int = Form(...),
#                                 data_type: str = Form(...), file_type: str = Form(...), save_dir: str = Form(...)):
#     response_data = {
#         "num_samples": num_samples,
#         "data_type": data_type,
#         "save_dir": save_dir
#     }
#     return JSONResponse(content=response_data)

# @app.websocket_route("/col-sim")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     form_data = await websocket.receive_json()

#     signal_length = int(form_data["signal_length"])
#     num_samples = int(form_data["num_samples"])
#     data_type = form_data["data_type"]
#     save_dir = form_data["save_dir"]
#     # return
            

#     frequency = 10.0  # Base frequency
#     count = 0
#     t = np.linspace(0, 2 * np.pi, signal_length)
    
#     data_saver = DataSaver(max_rows=num_samples, data_dir=save_dir, signal_type=data_type)

#     for i in range(num_samples):  # Reduced iterations for testing
#         start = time.time()
#         signal = [np.sin(2 * np.pi * frequency * t + i / 10) + np.random.randn(signal_length) * 0.2]
#         file_name, save_dir = data_saver.save_data(signal)

#         prediction = 0
#         if count == 5 or count == 6:
#             prediction = 1

#         if count < 5:
#             count += 1
#         else:
#             count = 0

#         # Change signal color based on prediction value
#         color = 'red' if prediction == 1 else 'blue'

#         # Prepare the signal data to be sent to the frontend
#         trace_signal = go.Scatter(x=t, y=signal[0], mode='lines', name='Signal', line=dict(color=color))
#         layout = go.Layout(title="Real-time Signal Plot", xaxis_title="Time", yaxis_title="Amplitude")
#         fig = go.Figure(data=[trace_signal], layout=layout)
#         graph_json = fig.to_json()

#         await websocket.send_json({"type": "graph", "data": graph_json})
    
#     file_num = 1

#     save_dir_size = get_dir_size(save_dir)
#     avlb_storage = get_available_disk_space(save_dir)
#     log_entry = {
#         "type": "log",
#         "fileNum": file_num,
#         "fileName": file_name,
#         "signalType": data_type,
#         "saveDir": save_dir,
#         "saveDirSize": save_dir_size,
#         "avlbStorage": avlb_storage
#     }
#     await websocket.send_json(log_entry)
#     await websocket.send_json({"type": "finished", "message": "Data collection Finished!"})


async def main():
    config = config = uvicorn.Config(app, host="localhost", port=8000, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()
   
if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Server stopped by user with Ctrl + C")