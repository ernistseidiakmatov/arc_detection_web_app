from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import plotly.graph_objs as go
import time
import numpy as np
import uvicorn
import asyncio
import ctypes
from collections import deque
import os 
import csv
from utils.predictor import *
from utils.db import DatabaseManager
from utils.plots import *
from utils.shared_state import SharedState



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/")
async def arc_detection(request: Request):
    return templates.TemplateResponse("arc_detection.html", {"request": request})


class SignalData(ctypes.Structure):
    _fields_ = [("data", ctypes.POINTER(ctypes.c_float)), ("size", ctypes.c_size_t)]

lib = ctypes.CDLL('./utils/lib_adc_signal.so')
lib.get_signal.restype = SignalData
state = SharedState()
@app.websocket_route("/arc-det")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            command = await websocket.receive_json()

            if "signal_length" in command:
                await state.update(signal_length=int(command["signal_length"]))
            
            if "save_arc_data" in command:
                await state.update(save_arc_data=int(command["save_arc_data"]))

            if "detection_period" in command:
                await state.update(detection_period=float(command["detection_period"]))
            
            if "save_dir" in command:
                await state.update(save_dir=str(command["save_dir"]))

            if "start" in command and command["start"]:
                await state.update(running=True)
                asyncio.create_task(data_collection_loop(websocket))

            if "stop" in command and command["stop"]:
                await state.update(running=False)
    except WebSocketDisconnect:
        print("WebSocket disconnected.")
        await state.update(running=False)

columns = ['mean', 'std', 'var', 'skewness', 'kurtosis', 'peak_to_peak', 'rms', 'dominant_freq', 'spectral_entropy']
signal_que = deque(maxlen=3)
predictor = SignalPredictor("lstm")
predictor.load_model()
scaller = get_scaler()
async def data_collection_loop(websocket: WebSocket):
    db = DatabaseManager()
    in_range = b"R6"
    size = ctypes.c_size_t(0)
    print("data collection called")
    filename = "arc_data_saved.csv"
    long_period = None
    long_predictions = None

    last_long_period = None
    try:
        while True:
            async with state.lock:
                if not state.running:
                    print("Stopping data collection.")
                    break
                signal_length = state.signal_length
                save_arc_data = state.save_arc_data
                detection_period =  state.detection_period
                save_dir = state.save_dir

            result_ptr = lib.get_signal()
            signals = [result_ptr.data[i] for i in range(result_ptr.size)]

            features_ = get_single_signal_feature(signals)
            sample = pd.DataFrame([features_], columns=columns)
            normalized_sample = scaller.transform(sample).reshape(1, 1, -1)
            pred_cls, prob = predictor.predict(normalized_sample)
            signal_que.append(pred_cls)
            if sum(signal_que) == 3:
                db.save_arc_prediction(1)
                if save_arc_data:
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    file_path = os.path.join(save_dir, filename)
                    try:
                        with open(file_path, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow(signals)  
                        print(f"Signals appended to {file_path}.")
                    except Exception as e:
                        print(f"Error writing to CSV: {e}")
            elif sum(signal_que) != 3:
                db.save_arc_prediction(0)
            t = np.arange(signal_length)
            color = 'red' if len(signal_que) == 3 and sum(signal_que) == 3 else 'blue'    

            timestamps, predictions = db.get_arc_predictions(detection_period)
            if timestamps and predictions:
                lower_graph_json = generate_lower_plot(timestamps, predictions)
            
            upper_graph_json = generate_signal_plot(signals, signal_length, color)

            await websocket.send_json({
                "type": "graph",
                "upper-data": upper_graph_json,
                "lower-data": lower_graph_json
            })
            
            await asyncio.sleep(0.08)
        db.close()
    except Exception as e:
        print(f"Error in data collection loop: {e}")

async def main():
    config = config = uvicorn.Config(app, host="localhost", port=8000, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()
   
if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Server stopped by user with Ctrl + C")