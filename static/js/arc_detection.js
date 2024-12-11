let startStopBtn = "Start";
let websocket = null;
let pendingDataQueue = []; // Queue to store data if WebSocket is not open yet

// function initializeWebSocket() {
//     if (websocket === null || websocket.readyState === WebSocket.CLOSED) {
//         websocket = new WebSocket("ws://localhost:8000/arc-det");

//         websocket.onopen = () => {
//             // Send all pending data from the queue
//             while (pendingDataQueue.length > 0) {
//                 const data = pendingDataQueue.shift();
//                 websocket.send(JSON.stringify(data));
//             }
//         };

//         websocket.onmessage = (event) => {
//             const message = JSON.parse(event.data);
//             if (message.type === "graph") {
//                 const graphData = JSON.parse(message.data);
//                 // graphData.layout.width = 1000; 
//                 Plotly.react('plotly-chart', graphData.data, graphData.layout);
//             } else if (message.type === "finished") {
//                 // console.log(message.message);
//             }
//         };

//         websocket.onclose = () => {
//             websocket = null; // Reset to allow reconnection if needed
//         };

//         websocket.onerror = (error) => {
//             console.error("WebSocket error:", error);
//         };
//     }
// }

// function startDetection() {
//     initializeWebSocket();

//     const formData = new FormData(document.getElementById("arcDetectionForm"));
//     const data = {
//         signal_length: formData.get('signal_length'),
//         save_arc_data: formData.get('save_arc_data'),
//         save_dir: formData.get('save_dir')
//     };

//     if (websocket.readyState === WebSocket.OPEN) {
//         websocket.send(JSON.stringify(data));
//     } else if (websocket.readyState === WebSocket.CONNECTING) {
//         // Queue the data to be sent once the WebSocket is open
//         pendingDataQueue.push(data);
//     } else {
//         pendingDataQueue.push(data);
//         initializeWebSocket();
//     }
// }

// let websocket = null; // Declare WebSocket as a global variable
// let pendingDataQueue = []; // Queue for messages to be sent when WebSocket is not ready

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

    if (isDetectionRunning) {
        stopDetection();
        button.textContent = "Start"; 
        button.classList.remove("stop");
        button.classList.add("start");
    } else {
        startDetection();
        button.textContent = "Stop";
        button.classList.remove("start");
        button.classList.add("stop");
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
        console.log("Detection started with signal length:", signal_length);
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
        console.log("Detection stopped.");
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
    console.log(saveDirElement);
    if (!saveDirElement) {
        console.error("Element with id 'save_dir' not found!");
    } else {
        const save_dir = saveDirElement.value || "/dataset/";
        console.log(save_dir);
    }
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
        console.log("Signal length updated to:", signal_length);
    } else if (websocket && websocket.readyState === WebSocket.CONNECTING) {
        pendingDataQueue.push(data);
    } else {
        console.error("WebSocket is not ready. Unable to update signal length.");
    }
}