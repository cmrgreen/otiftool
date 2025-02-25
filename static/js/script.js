//correct just take time in in itial calling of machine data function
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

// Populate the machine table with data from the backend
// function populateMachineTable(data) {
//     const tableBody = document.querySelector("#machineTable tbody");
//     tableBody.innerHTML = data
//         .map(
//             (machine) => `
//         <tr>
//             <td>${machine.Sensor_No}</td>
//             <td>${machine.Machine_No}</td>
//             <td>${machine.Level_MM}</td>
//             <td>${
//                 machine.Metal_Available_KG 
//             }</td>  <!-- Metal Available (KG) -->
//             <td>${machine.Consumption_Rate }</td>
//             <td>${machine.Refilling_Time}</td>
//             <td>${machine.Otif_per}</td>
//             <td>${machine.Availability_per}</td>
//             <td>${machine.W_Condition}</td>
//             <td>${machine.Status}</td>
//         </tr>
//     `
//         )
//         .join("");
// }

function populateMachineTable(data) {
    const tableBody = document.querySelector("#machineTable tbody");
    tableBody.innerHTML = data
        .map(
            (machine) => {
                // // Set background color for Working Condition cell
                // let workingConditionStyle = "";
                // if (machine.W_Condition === "Running") {
                //     workingConditionStyle = "background-color: lightgreen;";
                // } else if (machine.W_Condition === "Stopped") {
                //     workingConditionStyle = "background-color: lightcoral;";
                // }

                // Set background color for Working Condition box
                let workingConditionStyle = "";
                let workingConditionText = machine.W_Condition;
                if (machine.W_Condition === "Running") {
                    workingConditionStyle = "border: 2px solid green; color: green; padding: 5px;"; // Green border for Running
                } else if (machine.W_Condition === "Stopped") {
                    workingConditionStyle = "border: 2px solid red; color: red; padding: 5px;"; // Red border for Stopped
                }

                
                // Set text for Working Condition box
                // let workingConditionStyle = "";
                // let workingConditionText = machine.W_Condition;
                // if (machine.W_Condition === "Running") {
                //     workingConditionStyle = "border: 2px solid green; color: green; padding: 5px; display: block; text-align: center; width: fit-content; margin: 0 auto;"; // Green border for Running
                // } else if (machine.W_Condition === "Stopped") {
                //     workingConditionStyle = "border: 2px solid red; color: red; padding: 5px; display: block; text-align: center; width: fit-content; margin: 0 auto;"; // Red border for Stopped
                // }
                


                // Set text color for OTIF column
                let otifStyle = "";
                if (parseFloat(machine.Otif_per) === 100.00) {
                    otifStyle = "color: darkgreen;";  // Dark green for 100.00%
                } else if (parseFloat(machine.Otif_per) < 100.00) {
                    otifStyle = "color: red;";  // Red for values below 100.00%
                }

                // Set background color for Availability (%) column based on Level_MM
                let availabilityStyle = "";
                const levelMM = parseFloat(machine.Level_MM); // Convert Level_MM to number
                if (levelMM < 285) {
                    availabilityStyle = "background-color: #f0633c;";  // Red for Level_MM < 285
                } else if (levelMM >= 285 && levelMM <= 399) {
                    availabilityStyle = "background-color: #f2e63a;";  // Yellow for 285 <= Level_MM <= 399
                } else if (levelMM >= 399) {
                    availabilityStyle = "background-color: #48db83;";  // Yellow for 399 < Level_MM <= 570
                }

                return `
                    <tr>
                        <td>${machine.Sensor_No}</td>
                        <td>${machine.Machine_No}</td>
                        <td>${machine.Level_MM}</td>
                        <td>${machine.Metal_Available_KG}</td>  <!-- Metal Available (KG) -->
                        <td>${machine.Consumption_Rate}</td>
                        <td>${machine.Refilling_Time}</td>
                        <td style="${otifStyle}">${machine.Otif_per}%</td> <!-- OTIF column with color change -->
                        <td style="${availabilityStyle}">${machine.Availability_per}%</td> <!-- Availability column with background color -->
                        <td style="${workingConditionStyle}">${machine.W_Condition}</td> <!-- Working Condition with background color -->
                        <td>${machine.Status}</td>
                    </tr>
                `;
            }
        )
        .join("");
}



// Update the Overall Consumption Rate box with fetched data
function updateConsumptionRate(data) {
    const consumptionRateElement = document.querySelectorAll(".info-box p")[0]; // First info-box <p> tag
    if (data && data.consumption_rate) {
        consumptionRateElement.innerText = `${data.consumption_rate} KG/HRS`; // Set the value inside the <p> tag
    } else {
        consumptionRateElement.innerText = "No data available"; // Fallback if no data is found
    }
}

// Update the Total Machines Running box with fetched data
function updateTotalMachinesRunning(data) {
    const totalMachinesElement = document.querySelectorAll(".info-box p")[1]; // Third info-box <p> tag
    if (data && data.cntrun) {
        totalMachinesElement.innerText = data.cntrun; // Set the value inside the <p> tag
    } else {
        totalMachinesElement.innerText = "0"; // Fallback if no data is found
    }
}

// Update the Overall OTIF % box with fetched data
function updateOtifPercentage(data) {
    const otifElement = document.querySelectorAll(".info-box p")[2]; // Fourth info-box <p> tag
    if (data && data.otif) {
        otifElement.innerText = `${data.otif}%`; // Set the value inside the <p> tag
    } else {
        otifElement.innerText = "No data available"; // Fallback if no data is found
    }
}

async function fetchData() {
    try {
        const response = await fetch(
            "https://otif-tool.onrender.com/api/fetch_data"
        ); // Adjusted URL for API
        const data = await response.json();
        updateConsumptionRate(data["consumption_rate_data"]);
        updateTotalMachinesRunning(data["total_machines_data"]);
        updateOtifPercentage(data["otif_data_round"]);
        populateMachineTable(data["machine_data"]);
    } catch (error) {
        console.error("Error fetching machine data:", error);
    }
}

fetchData();
setInterval(fetchData, 60000);
