# main.py
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import plotly.graph_objs as go
import time
import numpy as np
import uvicorn
from utils.data_saver import *
from utils.storage import *
from utils.predictor import *
from utils.db import DatabaseManager
from utils.plots import *
import asyncio
import ctypes
from utils.shared_state import SharedState
from collections import deque 
import random
import os 
import csv



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
 return templates.TemplateResponse("index.html", {"request": request})

@app.get("/data-collection")
async def data_collection(request: Request):
    return templates.TemplateResponse("data_collection.html", {"request": request})

@app.post("/data-collection")
async def handle_data_collection(request: Request, signal_length: int = Form(...), 
                                 num_samples: int = Form(...), data_type: str = Form(...), 
                                 file_type: str = Form(...), save_dir: str = Form(...)):
    

    # # Just for testing: Returning an alert of the received form input
    # return templates.TemplateResponse(
    #     "data_collection.html", 
    #     {"request": request, 
    #      "alert": f"Received: Signal Length={signal_length}, Number of samples={num_samples}, Data type={data_type}, File type={file_type}, Save dir={save_dir}"
    #     }
    # )
    response_data = {
        "signal_length": signal_length,
        "num_samples": num_samples,
        "data_type": data_type,
        "file_type": file_type,
        "save_dir": save_dir
    }
    return JSONResponse(content=response_data)

@app.websocket_route("/col-sim")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    form_data = await websocket.receive_json()

    signal_length = int(form_data["signal_length"])
    num_samples = int(form_data["num_samples"])
    data_type = form_data["data_type"]
    save_dir = form_data["save_dir"]
    # return
            

    frequency = 10.0  # Base frequency
    count = 0
    t = np.linspace(0, 2 * np.pi, signal_length)
    
    data_saver = DataSaver(max_rows=num_samples, data_dir=save_dir, signal_type=data_type)

    for i in range(num_samples):  # Reduced iterations for testing
        start = time.time()
        signal = [np.sin(2 * np.pi * frequency * t + i / 10) + np.random.randn(signal_length) * 0.2]
        file_name, save_dir = data_saver.save_data(signal)

        prediction = 0
        if count == 5 or count == 6:
            prediction = 1

        if count < 5:
            count += 1
        else:
            count = 0

        # Change signal color based on prediction value
        color = 'red' if prediction == 1 else 'blue'

        # Prepare the signal data to be sent to the frontend
        trace_signal = go.Scatter(x=t, y=signal[0], mode='lines', name='Signal', line=dict(color=color))
        layout = go.Layout(title="Real-time Signal Plot", xaxis_title="Time", yaxis_title="Amplitude")
        fig = go.Figure(data=[trace_signal], layout=layout)
        graph_json = fig.to_json()

        await websocket.send_json({"type": "graph", "data": graph_json})
    
    file_num = 1

    save_dir_size = get_dir_size(save_dir)
    avlb_storage = get_available_disk_space(save_dir)
    log_entry = {
        "type": "log",
        "fileNum": file_num,
        "fileName": file_name,
        "signalType": data_type,
        "saveDir": save_dir,
        "saveDirSize": save_dir_size,
        "avlbStorage": avlb_storage
    }
    await websocket.send_json(log_entry)
    await websocket.send_json({"type": "finished", "message": "Data collection Finished!"})


@app.get("/arc-detection")
async def arc_detection(request: Request):
    return templates.TemplateResponse("arc_detection.html", {"request": request})



# Load the shared library 
lib = ctypes.CDLL('./utils/lib_signle.so')
lib.get_signal.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
lib.get_signal.restype = ctypes.POINTER(ctypes.c_float)
state = SharedState()
@app.websocket_route("/arc-det")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()

#     form_data = await websocket.receive_json()
#     signal_length = int(form_data["signal_length"])
#     save_arc_data = bool(form_data["save_arc_data"])
#     save_dir = form_data["save_dir"]
#     await websocket.send_json({"type": "finished", "message": "Data collection Finished!"})

#     signals = get_dataset()
#     np.random.shuffle(signals)
#     features = np.array([get_single_signal_feature(signal) for signal in signals])
    
    # predictor = SignalPredictor("lstm")
    # predictor.load_model()
#     t = np.arange(2048)
#     count_ = 0
#     scaller = get_scaler()
    
#     for i, sample in enumerate(features[:]):
        # columns = ['mean', 'std', 'var', 'skewness', 'kurtosis', 'peak_to_peak', 'rms', 'dominant_freq', 'spectral_entropy']
        # sample = pd.DataFrame(sample.reshape(1, -1), columns=columns)
        # normalized_sample = scaller.transform(sample)
        # normalized_sample.reshape(1, 1, normalized_sample.shape[1])
#         predicted_class, probabilities = predictor.predict(normalized_sample)
#         res = {"prediction": predicted_class}
#         color = 'red' if predicted_class == 1 else 'blue'
#         if predicted_class == 0:
#             count_ += 1

#         trace_signal = go.Scatter(x=t, y=signals[i][:], mode='lines', name='Signal', line=dict(color=color))
#         layout = go.Layout(title=f"Real-time Signal Plot {i+1}", xaxis_title="Time", yaxis_title="Amplitude")
#         fig = go.Figure(data=[trace_signal], layout=layout)
#         graph_json = fig.to_json()
        
#         await websocket.send_json({"type": "graph", "data": graph_json})
#         await asyncio.sleep(0.08)
#     await websocket.close()
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Listen for commands from the client
    try:
        while True:
            command = await websocket.receive_json()
            print(command)

            if "signal_length" in command:
                # Update signal length
                await state.update(signal_length=int(command["signal_length"]))
            
            if "save_arc_data" in command:
                # Update signal length
                await state.update(save_arc_data=int(command["save_arc_data"]))

            if "detection_period" in command:
                # Update signal length
                await state.update(detection_period=float(command["detection_period"]))
            
            if "save_dir" in command:
                # Update signal length
                await state.update(save_dir=str(command["save_dir"]))

            if "start" in command and command["start"]:
                # Start data collection
                await state.update(running=True)
                asyncio.create_task(data_collection_loop(websocket))

            if "stop" in command and command["stop"]:
                # Stop data collection
                await state.update(running=False)
    except WebSocketDisconnect:
        print("WebSocket disconnected.")
        await state.update(running=False)

# Data collection loop
columns = ['mean', 'std', 'var', 'skewness', 'kurtosis', 'peak_to_peak', 'rms', 'dominant_freq', 'spectral_entropy']
# t = np.arange(2048)
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
            

            # Collect signals
            # lib.get_signal(1, output_buffer, ctypes.byref(out_size))
            
            result_ptr = lib.get_signal(in_range, ctypes.byref(size))
            # signals = [result_ptr[i] for i in range(size_value)]
            signals = np.ctypeslib.as_array(result_ptr, shape=(size.value,))

            features_ = get_single_signal_feature(signals)
            sample = pd.DataFrame([features_], columns=columns)
            normalized_sample = scaller.transform(sample).reshape(1, 1, -1)
            pred_cls, prob = predictor.predict(normalized_sample)
            signal_que.append(pred_cls)
            # random_pred = random.randint(0, 1)
            # signal_que.append(random_pred)
            if sum(signal_que) == 3:
                db.save_arc_prediction(1)
                if save_arc_data:
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                file_path = os.path.join(save_dir, filename)
                try:
                    with open(file_path, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(signals)  # Write signals as a row
                    print(f"Signals appended to {file_path}.")
                except Exception as e:
                    print(f"Error writing to CSV: {e}")
            elif sum(signal_que) != 3:
                db.save_arc_prediction(0)
            # Adjust x-axis for the given signal length
            t = np.arange(signal_length)
            # if random_pred == sum:
            color = 'red' if len(signal_que) == 3 and sum(signal_que) == 3 else 'blue'    
            print(detection_period)
            print(state.detection_period)

            print(last_long_period)
            if long_period and long_period:
                print(long_predictions[:2])
                print(long_period[:2])
            if detection_period <= 10:
                timestamps, predictions = db.get_arc_predictions(detection_period)
                if timestamps and predictions:
                    lower_graph_json = generate_lower_plot(timestamps, predictions)
            # else:
            #     # Check if the detection period has changed
            #     if last_long_period != detection_period:
            #         long_period, long_predictions = db.get_arc_predictions(detection_period)
            #         last_long_period = detection_period
            #         if long_period and long_predictions:
            #             lower_graph_json = generate_lower_plot(long_period, long_predictions)
            upper_graph_json = generate_signal_plot(signals, signal_length, color)

            # Send the signal to the client
            await websocket.send_json({
                "type": "graph",
                "upper-data": upper_graph_json,
                "lower-data": lower_graph_json
            })
            
            # Simulate real-time processing delay
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