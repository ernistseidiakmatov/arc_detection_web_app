let startStopBtn = "Start";
let websocket = null;
let pendingDataQueue = []; // Queue to store data if WebSocket is not open yet

function initializeWebSocket() {
    if (websocket === null || websocket.readyState === WebSocket.CLOSED) {
        websocket = new WebSocket("ws://localhost:8000/arc-det");

        websocket.onopen = () => {
            // Send all pending data from the queue
            while (pendingDataQueue.length > 0) {
                const data = pendingDataQueue.shift();
                websocket.send(JSON.stringify(data));
            }
        };

        websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === "graph") {
                const graphData = JSON.parse(message.data);
                // graphData.layout.width = 1000; 
                Plotly.react('plotly-chart', graphData.data, graphData.layout);
            } else if (message.type === "finished") {
                // console.log(message.message);
            }
        };

        websocket.onclose = () => {
            websocket = null; // Reset to allow reconnection if needed
        };

        websocket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }
}

function startDetection() {
    initializeWebSocket();

    const formData = new FormData(document.getElementById("arcDetectionForm"));
    const data = {
        signal_length: formData.get('signal_length'),
        save_arc_data: formData.get('save_arc_data'),
        save_dir: formData.get('save_dir')
    };

    if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(data));
    } else if (websocket.readyState === WebSocket.CONNECTING) {
        // Queue the data to be sent once the WebSocket is open
        pendingDataQueue.push(data);
    } else {
        pendingDataQueue.push(data);
        initializeWebSocket();
    }
}