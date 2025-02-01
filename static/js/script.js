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

// Similar updates for the other fetch functions...
