

function startCollection() {
    // alert('Data collection started!');
    const formData = new FormData(document.getElementById("dataCollectionForm"));
    const data = {
        signal_length: formData.get('signal_length'),
        num_samples: formData.get('num_samples'),
        data_type: formData.get('data_type'),
        file_type: formData.get('file_type'),
        save_dir: formData.get('save_dir')
    };

    console.log(data)
    const hi = {
        msg: "hello world"
    }
    const websocket = new WebSocket("ws://localhost:8000/col-sim");
    websocket.onopen = () => {
        websocket.send(JSON.stringify(data));
    };

    websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === "graph") {
            const graphData = JSON.parse(message.data);
            // console.log("recieved graph", graphData);
            Plotly.newPlot('plotly-chart', graphData.data, graphData.layout);
        } else if (message.type === "log") {
            addLogEntry(message.fileNum, message.fileName, message.signalType, message.saveDir, message.saveDirSize, message.avlbStorage);
            // console.log("recieved log", message.fileName);
        } else if (message.type === "finished") {
            console.log(message.message);
            // alert(message.message);
        }
    };
};

let fileCount = 0

function addLogEntry(fileNum, fileName, signalType, saveDir, saveDirSize, avlbStorage) {
    const logTableBody = document.getElementById("logTableBody");
    const newRow = document.createElement("tr");
    fileCount += 1
    newRow.innerHTML = `
        <td class="col-file-num">${fileCount}</td>
        <td class="col-file-name">${fileName ? fileName.substring(0, 7) : 'N/A'}</td>
        <td class="col-signal-type">${signalType || 'N/A'}</td>
        <td class="col-save-dir">${saveDir || 'N/A'}</td>
        <td class="col-dir-size">${saveDirSize || 'N/A'}</td>
        <td class="col-avlb-storage">${avlbStorage || 'N/A'}</td>
    `;
    logTableBody.appendChild(newRow);
    logTableBody.scrollTop = logTableBody.scrollHeight;
}


// var socket = new WebSocket("ws://localhost:8000/col-sim");
// socket.onmessage = function(event) {
//     var graphData = JSON.parse(event.data);
//     Plotly.newPlot('plotly-chart', graphData.data, graphData.layout);
// };