let startStopBtn = "Start";
let websocket = null;
let pendingDataQueue = [];


function initializeWebSocket() {
    if (websocket === null || websocket.readyState === WebSocket.CLOSED) {
        websocket = new WebSocket("ws://localhost:8000/arc-det");

        websocket.onopen = () => {
            console.log("WebSocket connection established.");
            while (pendingDataQueue.length > 0) {
                const data = pendingDataQueue.shift();
                websocket.send(JSON.stringify(data));
            }
        };

        websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === "graph") {
                const upperGraphData = JSON.parse(message["upper-data"]);
                Plotly.react('upper-plotly-chart', upperGraphData.data, upperGraphData.layout);
                const lowerGraphData = JSON.parse(message["lower-data"]);
                Plotly.react('lower-plotly-chart', lowerGraphData.data, lowerGraphData.layout);
            } else if (message.type === "finished") {
                console.log(message.message);
            }
        }

        websocket.onclose = () => {
            console.warn("WebSocket connection closed.");
            websocket = null;
        };

        websocket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }
}

let isDetectionRunning = false;
function toggleDetection() {
    const button = document.getElementById("toggleBtn");
    const updateButton = document.getElementById("updateBtn"); // Get the update button

    if (isDetectionRunning) {
        stopDetection();
        button.textContent = "Start"; 
        button.classList.remove("stop");
        button.classList.add("start");

        // Disable the Update button
        updateButton.disabled = true;
    } else {
        startDetection();
        button.textContent = "Stop";
        button.classList.remove("start");
        button.classList.add("stop");

        // Enable the Update button
        updateButton.disabled = false;
    }

    isDetectionRunning = !isDetectionRunning;
}

function startDetection() {
    initializeWebSocket();

    const signal_length = document.getElementById("signal_length").value || 2048;
    const save_arc_data = document.getElementById("save_arc_data").value || 0;
    const saveDirElement = document.getElementById("save_dir");
    let save_dir = "/home/netvision/Desktop/arc_data";

    if (!saveDirElement) {
        console.error("Element with id 'save_dir' not found!");
    } else {
        const inputValue = saveDirElement.value.trim();
        save_dir = inputValue || save_dir;  
    }

    const detection_period = parseFloat(document.getElementById("detection_period")?.value) || 0.5;

    const data = {
        start: true,
        signal_length: parseInt(signal_length, 10),
        save_arc_data: parseInt(save_arc_data, 10),
        save_dir: save_dir, 
        detection_period: detection_period,
    };

    if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(data));
    } else if (websocket.readyState === WebSocket.CONNECTING) {

        pendingDataQueue.push(data);
    } else {
        console.error("WebSocket is not ready. Unable to start detection.");
    }
}

function stopDetection() {
    initializeWebSocket();

    const data = {
        stop: true,
    };

    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(data));
    } else if (websocket && websocket.readyState === WebSocket.CONNECTING) {
        pendingDataQueue.push(data);
    } else {
        console.error("WebSocket is not ready. Unable to stop detection.");
    }
}

function updateSignalLength() {
    initializeWebSocket();

    const signal_length = document.getElementById("signal_length").value || 2048;
    const save_arc_data = document.getElementById("save_arc_data").value || 0;
    const saveDirElement = document.getElementById("save_dir").value;
    
    const save_dir = saveDirElement.value || "/home/netvision/Desktop/arc_data";
    console.log(save_dir);
    
    const detection_period = document.getElementById("detection_period").value || 0.5;

    const data = {
        start: true,
        signal_length: parseInt(signal_length),
        save_arc_data: parseInt(save_arc_data),
        save_dir: save_dir.toString(),
        detection_period: parseFloat(detection_period)
    };

    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(data));
    } else if (websocket && websocket.readyState === WebSocket.CONNECTING) {
        pendingDataQueue.push(data);
    } else {
        console.error("WebSocket is not ready. Unable to update signal length.");
    }
}