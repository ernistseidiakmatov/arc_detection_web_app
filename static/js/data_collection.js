
let fileCount = 0

function addLogEntry(fileName, signalType, saveDir, saveDirSize, avlbStorage) {
    const logTableBody = document.getElementById("logTableBody");
    const newRow = document.createElement("tr");
    console.log("Add Log Entyry");
    console.log(fileName, signalType, saveDir, saveDirSize, avlbStorage);
    fileCount += 1
    newRow.innerHTML = `
        <td class="col-file-num">${fileCount}</td>
        <td class="col-file-name">${fileName || 'N/A'}</td>
        <td class="col-signal-type">${signalType || 'N/A'}</td>
        <td class="col-save-dir">${saveDir || 'N/A'}</td>
        <td class="col-dir-size">${saveDirSize || 'N/A'}</td>
        <td class="col-avlb-storage">${avlbStorage || 'N/A'}</td>
    `;
    logTableBody.appendChild(newRow);
    logTableBody.scrollTop = logTableBody.scrollHeight;
}

function startCollection() {
    const formData = new FormData(document.getElementById("dataCollectionForm"));
    const numSamples = parseInt(formData.get("num_samples"));
    const data = {
        num_samples: numSamples,
        data_type: formData.get("data_type"),
        save_dir: formData.get("save_dir") || "/home/netvision/Desktop/datasets/"
    };

    const progressBarContainer = document.getElementById("progressBarContainer");
    const progressBar = document.getElementById("progressBar");
    const progressText = document.getElementById("progressText");
    const statsTable = document.getElementById("statsTable");
    
    progressBarContainer.style.display = "block";
    statsTable.style.display = "none";
    progressBar.value = 0;
    progressText.textContent = "0%";

    const totalTimeEstimate = 16.65 * numSamples;
    let elapsedTime = 0;

    const progressInterval = setInterval(() => {
        elapsedTime += 100;
        const progress = Math.min((elapsedTime / totalTimeEstimate) * 100, 99);
        progressBar.value = progress;
        progressText.textContent = `${Math.round(progress)}%`;
        
        if (progress >= 90) {
            elapsedTime += 100; 
        }
    }, 100);

    fetch("/start-collection", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    }).then(response => response.json()).then(result => {
        clearInterval(progressInterval);
        progressBar.value = 100;
        progressText.textContent = "100%";

        if (result.status === "success") {
            if (result) {
                addLogEntry(
                    result.file_name,
                    result.data_type,
                    result.save_dir,
                    result.dir_size,
                    result.avlb_storage
                );

                const tableBody = document.querySelector("#statsTable tbody");
                tableBody.innerHTML = "";

                for (const [key, value] of Object.entries(result.stats)) {
                    const row = tableBody.insertRow();
                    const cellKey = row.insertCell(0);
                    const cellValue = row.insertCell(1);
                    cellKey.textContent = key;
                    cellKey.classList.add("stat-cell");
                    cellValue.textContent = value;
                }
            }
            console.log(result.message);
            console.log(result);
        } else {
            console.error("error", result.message);
        }
    }).catch(error => {
        clearInterval(progressInterval);
        console.error("Error", error);
    }).finally(() => {
        setTimeout(() => {
            progressBarContainer.style.display = "none";
            statsTable.style.display = "table";
        }, 1000);
    });
}


function transferDataset() {
    const formData = new FormData(document.getElementById("dataCollectionForm"));
    const numSamples = parseInt(formData.get("num_samples"));
    const data = {
        save_dir: formData.get("save_dir") || "/home/netvision/Desktop/datasets/"
    };

    fetch("/transfer-dataset", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    }).then(response => response.json()).then(result => {
        if (result.status === "success") {
            console.log(result)
            if (result) {
                alert(result.message);
            }
        } else {
            console.log(result)
            alert(result.message);
        }
    });
}