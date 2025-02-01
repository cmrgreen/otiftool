function updateDateTime() {
    const now = new Date();
    const date = now.toLocaleDateString("en-US", {
        weekday: "long",
        month: "short",
        day: "numeric",
        year: "numeric",
    });
    const time = now.toLocaleTimeString("en-US", {
        hour12: true,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });

    document.getElementById("datetime").innerHTML = `${date} | ${time}`;
}

setInterval(updateDateTime, 1000);
updateDateTime();

async function fetchMachineData() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/machine_data"
        );
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        populateMachineTable(data);
    } catch (error) {
        console.error("Error fetching machine data:", error.message);
    }
}

function populateMachineTable(data) {
    const tableBody = document.querySelector("#machineTable tbody");
    tableBody.innerHTML = data
        .map(
            (machine) => `
        <tr>
            <td>${machine.Sensor_No}</td>
            <td>${machine.Machine_No}</td>
            <td>${machine.Level_MM}</td>
            <td>${machine.Metal_Available_KG || "N/A"}</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td>${machine.W_Condition}</td>
            <td>${machine.Status}</td>
        </tr>
    `
        )
        .join("");
}

async function fetchOverallConsumptionRate() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/overall_consumption_rate"
        );
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        updateConsumptionRate(data);
    } catch (error) {
        console.error(
            "Error fetching overall consumption rate data:",
            error.message
        );
    }
}

function updateConsumptionRate(data) {
    const consumptionRateElement = document.querySelectorAll(".info-box p")[0];
    if (data && data.Molten_Target) {
        consumptionRateElement.innerText = data.Molten_Target;
    } else {
        consumptionRateElement.innerText = "No data available";
    }
}

async function fetchMoltenTarget() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/molten_target"
        );
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        updateMoltenTarget(data);
    } catch (error) {
        console.error("Error fetching molten target data:", error.message);
    }
}

function updateMoltenTarget(data) {
    const moltenTargetElement = document.querySelectorAll(".info-box p")[1];
    if (data && data.Molten_Target) {
        moltenTargetElement.innerText = data.Molten_Target;
    } else {
        moltenTargetElement.innerText = "No data available";
    }
}

async function fetchTotalMachinesRunning() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/total_machines_running"
        );
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        updateTotalMachinesRunning(data);
    } catch (error) {
        console.error(
            "Error fetching total machines running data:",
            error.message
        );
    }
}

async function fetchOtifPercentage() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/otif_percentage"
        );
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        updateOtifPercentage(data);
    } catch (error) {
        console.error("Error fetching OTIF percentage data:", error.message);
    }
}

function updateOtifPercentage(data) {
    const otifElement = document.querySelectorAll(".info-box p")[3];
    if (data && data.Molten_Target) {
        otifElement.innerText = `${data.Molten_Target}%`;
    } else {
        otifElement.innerText = "No data available";
    }
}

fetchMachineData();
fetchOverallConsumptionRate();
fetchMoltenTarget();
fetchTotalMachinesRunning();
fetchOtifPercentage();
