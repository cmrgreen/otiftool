//     function updateDateTime() {
//         // Get current date and time
//         const now = new Date();

//         // Format the date (e.g., "Feb 01, 2025")
//         const date = now.toLocaleDateString('en-US', {
//             weekday: 'long', // e.g., "Monday"
//             month: 'short',  // e.g., "Feb"
//             day: 'numeric',  // e.g., "1"
//             year: 'numeric'  // e.g., "2025"
//         });

//         // Format the time (e.g., "12:45:30 PM")
//         const time = now.toLocaleTimeString('en-US', {
//             hour12: true, // 12-hour format
//             hour: '2-digit',
//             minute: '2-digit',
//             second: '2-digit'
//         });

//         // Update the datetime element
//         document.getElementById('datetime').innerHTML = `${date} | ${time}`;
//     }

//     // Update the date and time every second
//     setInterval(updateDateTime, 1000);

//     // Call the function initially to show time immediately when the page loads
//     updateDateTime();

// // Fetch machine data from the backend
// async function fetchMachineData() {
//     try {
//         const response = await fetch('https://otif-tool.onrender.com/api/machine_data'); // Adjusted URL for API
//         const data = await response.json();
//         populateMachineTable(data);
//     } catch (error) {
//         console.error('Error fetching machine data:', error);
//     }
// }

// // Populate the machine table with data from the backend
// function populateMachineTable(data) {
//     const tableBody = document.querySelector('#machineTable tbody');
//     tableBody.innerHTML = data.map(machine => `
//         <tr>
//              <td>${machine.Sensor_No}</td>
//             <td>${machine.Machine_No}</td>
//             <td>${machine.Level_MM}</td>
//              <td>${machine.Metal_Available_KG || 'N/A'}</td>  <!-- Metal Available (KG) -->

//             <td></td>
//             <td></td>
//             <td></td>
//             <td></td>
//             <td>${machine.W_Condition}</td>
//             <td>${machine.Status}</td>
//         </tr>
//     `).join('');
// }

// // Fetch machine data when the page loads
// fetchMachineData();

function updateDateTime() {
    // Get current date and time
    const now = new Date();

    // Format the date (e.g., "Feb 01, 2025")
    const date = now.toLocaleDateString("en-US", {
        weekday: "long", // e.g., "Monday"
        month: "short", // e.g., "Feb"
        day: "numeric", // e.g., "1"
        year: "numeric", // e.g., "2025"
    });

    // Format the time (e.g., "12:45:30 PM")
    const time = now.toLocaleTimeString("en-US", {
        hour12: true, // 12-hour format
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });

    // Update the datetime element
    document.getElementById("datetime").innerHTML = `${date} | ${time}`;
}

// Update the date and time every second
setInterval(updateDateTime, 1000);

// Call the function initially to show time immediately when the page loads
updateDateTime();

// Fetch machine data from the backend
async function fetchMachineData() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/machine_data"
        ); // Adjusted URL for API
        const data = await response.json();
        populateMachineTable(data);
    } catch (error) {
        console.error("Error fetching machine data:", error);
    }
}

// Populate the machine table with data from the backend
function populateMachineTable(data) {
    const tableBody = document.querySelector("#machineTable tbody");
    tableBody.innerHTML = data
        .map(
            (machine) => `
        <tr>
            <td>${machine.Sensor_No}</td>
            <td>${machine.Machine_No}</td>
            <td>${machine.Level_MM}</td>
            <td>${
                machine.Metal_Available_KG || "N/A"
            }</td>  <!-- Metal Available (KG) -->
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

// Fetch data for Overall Consumption Rate
async function fetchOverallConsumptionRate() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/overall_consumption_rate"
        ); // Adjusted URL for API
        const data = await response.json();
        updateConsumptionRate(data); // Update the UI with the fetched data
    } catch (error) {
        console.error("Error fetching overall consumption rate data:", error);
    }
}

// Update the Overall Consumption Rate box with fetched data
function updateConsumptionRate(data) {
    const consumptionRateElement = document.querySelectorAll(".info-box p")[0]; // First info-box <p> tag
    if (data && data.Molten_Target) {
        consumptionRateElement.innerText = `${data.Molten_Target} KG/HRS`; // Set the value inside the <p> tag
    } else {
        consumptionRateElement.innerText = "No data available"; // Fallback if no data is found
    }
}

// Fetch data for Molten Metal Target (Plant)
async function fetchMoltenTarget() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/molten_target"
        ); // Adjusted URL for API
        const data = await response.json();
        updateMoltenTarget(data); // Update the UI with the fetched data
    } catch (error) {
        console.error("Error fetching molten target data:", error);
    }
}

// Update the Molten Metal Target box with fetched data
function updateMoltenTarget(data) {
    const moltenTargetElement = document.querySelectorAll(".info-box p")[1]; // Second info-box <p> tag
    if (data && data.Molten_Target) {
        moltenTargetElement.innerText = data.Molten_Target; // Set the value inside the <p> tag
    } else {
        moltenTargetElement.innerText = "No data available"; // Fallback if no data is found
    }
}

// Fetch data for Total Machines Running
async function fetchTotalMachinesRunning() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/total_machines_running"
        ); // Adjusted URL for API
        const data = await response.json();
        updateTotalMachinesRunning(data); // Update the UI with the fetched data
    } catch (error) {
        console.error("Error fetching total machines running data:", error);
    }
}

// Update the Total Machines Running box with fetched data
function updateTotalMachinesRunning(data) {
    const totalMachinesElement = document.querySelectorAll(".info-box p")[2]; // Third info-box <p> tag
    if (data && data.Molten_Target) {
        totalMachinesElement.innerText = data.Molten_Target; // Set the value inside the <p> tag
    } else {
        totalMachinesElement.innerText = "No data available"; // Fallback if no data is found
    }
}

// Fetch data for Overall OTIF %
async function fetchOtifPercentage() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/otif_percentage"
        ); // Adjusted URL for API
        const data = await response.json();
        updateOtifPercentage(data); // Update the UI with the fetched data
    } catch (error) {
        console.error("Error fetching OTIF percentage data:", error);
    }
}

// Update the Overall OTIF % box with fetched data
function updateOtifPercentage(data) {
    const otifElement = document.querySelectorAll(".info-box p")[3]; // Fourth info-box <p> tag
    if (data && data.Molten_Target) {
        otifElement.innerText = `${data.Molten_Target}%`; // Set the value inside the <p> tag
    } else {
        otifElement.innerText = "No data available"; // Fallback if no data is found
    }
}

// Fetch machine data when the page loads
fetchMachineData();

setInterval(fetchMachineData, 60000);

fetchOverallConsumptionRate();
fetchMoltenTarget();
fetchTotalMachinesRunning();
fetchOtifPercentage();
