from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
import time
import threading
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': '45.248.62.117',
    'user': 'vishal',
    'password': 'vishal@123',
    'database': 'cmr_db',
    'port': 3306
}

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Function to get a database connection with retries
def get_db_connection_with_retry():
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            conn = mysql.connector.connect(**db_config)
            if conn.is_connected():
                return conn
        except Error as e:
            attempts += 1
            print(f"Attempt {attempts}/{MAX_RETRIES} failed to connect to the database: {e}")
            if attempts < MAX_RETRIES:
                time.sleep(RETRY_DELAY)  # Wait before retrying
            else:
                raise Exception("Max retries reached. Could not connect to the database.")

    return None  # If all retries fail


# Function to fetch latest data from a specific table
def fetch_latest_data_from_table(number):
    conn = get_db_connection_with_retry()
    cursor = conn.cursor(dictionary=True)
    query = f"SELECT * FROM S{number}_Data WHERE STR_TO_DATE(Date, '%d-%m-%Y') = CURDATE() ORDER BY time DESC LIMIT 1;"
    cursor.execute(query)
    latest_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return latest_data

# Function to fetch Metal Available (KG) from Material_Weight_Factor
def fetch_metal_available_data(number):
    conn = get_db_connection_with_retry()
    cursor = conn.cursor(dictionary=True)
    query = f"""
    SELECT 
        ROUND((mw.Weight_per_mm * s{number}_Data.Level_MM), 2) AS metalavailinkg
    FROM Material_Weight_Factor mw
    LEFT JOIN S{number}_Data S{number}_Data on s{number}_Data.Machine_No = mw.Machine_No
    WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
    ORDER BY s{number}_Data.Time DESC
    LIMIT 1;
    """
    cursor.execute(query)
    metal_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return metal_data

# Function to fetch consumption rate from Material_Weight_Factor
def fetch_consumption_rate_data(number):
    conn = get_db_connection_with_retry()
    cursor = conn.cursor(dictionary=True)
    query = f"""
   SELECT 
    ROUND(
        (
            (SELECT SUM(change_level) * 2
             FROM (
                 SELECT change_level
                 FROM cmr_db.S{number}_Data 
                   WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
                 ORDER BY time DESC
                 LIMIT 30
             ) tmp
            ) ) * 
            (
                SELECT weight_per_mm
                FROM Material_Weight_Factor
                WHERE Sensor_No = {number}
                LIMIT 1
            ), 2
    ) AS consumption_rate;
    """
    cursor.execute(query)
    consumption_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return consumption_data

# Query for Availability%
def fetch_availability_per_data(number):
    conn = get_db_connection_with_retry()
    cursor = conn.cursor(dictionary=True)
    query = f"""
SELECT 
  (SELECT Level_MM FROM S{number}_Data LIMIT 1) / 
  (SELECT Furnace_Depth FROM Material_Weight_Factor WHERE Sensor_No = {number} LIMIT 1) AS availability_per;
    """
    cursor.execute(query)
    availability_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return availability_data

# Query for OTIF%
def fetch_otif_per_data(number):
    conn = get_db_connection_with_retry()
    cursor = conn.cursor(dictionary=True)
    query = f"""
SELECT COUNT(*) AS otif
FROM (
    SELECT * 
    FROM S{number}_Data 
    ORDER BY time DESC
    LIMIT 480
) AS tmp
WHERE Level_MM < (
    SELECT Low_Level 
    FROM Level_Limit 
    WHERE Sensor_No = {number}
)
AND W_Condition = 'Stopped';
    """
    cursor.execute(query)
    otif_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return otif_data

# Query for Refilling Time
def fetch_RefillingTime_data(number):
    conn = get_db_connection_with_retry()
    cursor = conn.cursor(dictionary=True)
    query = f"""
  SELECT 
    ROUND(
        (
            (SELECT SUM(change_level) * 3
             FROM (
                 SELECT change_level
                 FROM cmr_db.S{number}_Data 
                   WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
                 ORDER BY time DESC
                 LIMIT 100
             ) tmp
            ) ) * 
            (
                SELECT weight_per_mm
                FROM Material_Weight_Factor
                WHERE Sensor_No = {number}
                LIMIT 1
            ), 2
    ) AS Refilling_Time;
    """
    cursor.execute(query)
    refilling_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return refilling_data

# Route to fetch machine data
@app.route('/api/machine_data', methods=['GET'])
def get_machine_data():
    machine_data = []
    for index in range(1, 9):  # Looping through machine numbers 1 to 8
        # Fetch all machine-related data
        data = fetch_latest_data_from_table(index)
        metal_data = fetch_metal_available_data(index)
        consumption_data = fetch_consumption_rate_data(index)
        availability_data = fetch_availability_per_data(index)
        otif_data = fetch_otif_per_data(index)
        refilling_data = fetch_RefillingTime_data(index)
        
        if data:
            machine_info = {
                'Sensor_No': data['Sensor_No'],
                'Machine_No': data['Machine_No'],
                'Level_MM': data['Level_MM'],
                'W_Condition': data['W_Condition'],
                'Status': data['Status'],
                'Metal_Available_KG': metal_data['metalavailinkg'] if metal_data else None,
                'Consumption_Rate': consumption_data['consumption_rate'] if consumption_data else None,
                'Availability_per': availability_data['availability_per'] if availability_data else None,
                'Otif_per': otif_data['otif'] if otif_data else None,
                'Refilling_Time': refilling_data['Refilling_Time'] if refilling_data else None
            }
            machine_data.append(machine_info)
    
    return jsonify(machine_data)

# Route to fetch overall consumption rate
@app.route('/api/overall_consumption_rate', methods=['GET'])
def get_overall_consumption_rate():
    consumption_rate_data = fetch_consumption_rate_data(0)  # Provide a number for the rate query
    return jsonify(consumption_rate_data)

# Route to fetch molten target value
@app.route('/api/molten_target', methods=['GET'])
def get_molten_target():
    molten_target_data = fetch_molten_target()  # Use the appropriate function
    return jsonify(molten_target_data)

# Route to fetch total machines running
@app.route('/api/total_machines_running', methods=['GET'])
def get_total_machines_running():
    total_machines_data = fetch_total_machines_running()  # Use the correct function
    return jsonify(total_machines_data)

# Route to fetch overall OTIF percentage
@app.route('/api/otif_percentage', methods=['GET'])
def get_otif_percentage():
    otif_data = fetch_otif_percentage()  # Fetch the OTIF percentage
    return jsonify(otif_data)

# Route to render index.html
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
