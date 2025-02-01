from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
import time
import threading

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

# Connect to the database
def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Function to fetch latest data from a specific table
def fetch_latest_data_from_table(number):
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM S{number}_Data WHERE Date = '18-01-2025' ORDER BY time DESC LIMIT 1;"
        cursor.execute(query)
        latest_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return latest_data
    except Exception as e:
        print(f"Error fetching latest data for table S{number}: {e}")
        return None

# Function to fetch Metal Available (KG) from Material_Weight_Factor
def fetch_metal_available_data(number):
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        
        cursor = conn.cursor(dictionary=True)
        query = f"""
        SELECT 
            ROUND((mw.Weight_per_mm * s{number}.Level_MM), 2) AS metalavailinkg
        FROM Material_Weight_Factor mw
        LEFT JOIN S{number}_Data s{number} ON s{number}.Machine_No = mw.Machine_No
        WHERE s{number}.Date = '18-01-2025'
        ORDER BY s{number}.Time DESC
        LIMIT 1;
        """
        cursor.execute(query)
        metal_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return metal_data
    except Exception as e:
        print(f"Error fetching metal available data for table S{number}: {e}")
        return None

# Function to fetch Overall Consumption Rate
def fetch_overall_consumption_rate():
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT Molten_Target 
        FROM Plant_Target 
        WHERE Date = '19 October 2023 12:38:41' 
        ORDER BY Date DESC 
        LIMIT 1;
        """
        cursor.execute(query)
        consumption_rate_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return consumption_rate_data
    except Exception as e:
        print(f"Error fetching overall consumption rate: {e}")
        return None

# Function to fetch Molten Metal Target (Plant)
def fetch_molten_target():
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT Molten_Target 
        FROM Plant_Target 
        WHERE Date = '19 October 2023 12:38:41' 
        ORDER BY Date DESC 
        LIMIT 1;
        """
        cursor.execute(query)
        molten_target_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return molten_target_data
    except Exception as e:
        print(f"Error fetching molten target: {e}")
        return None

# Function to fetch Total Machines Running (dummy for now)
def fetch_total_machines_running():
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT Molten_Target 
        FROM Plant_Target 
        WHERE Date = '19 October 2023 12:38:41' 
        ORDER BY Date DESC 
        LIMIT 1;
        """
        cursor.execute(query)
        total_machines_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return total_machines_data
    except Exception as e:
        print(f"Error fetching total machines running: {e}")
        return None

# Function to fetch Overall OTIF % (dummy for now)
def fetch_otif_percentage():
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT Molten_Target 
        FROM Plant_Target 
        WHERE Date = '19 October 2023 12:38:41' 
        ORDER BY Date DESC 
        LIMIT 1;
        """
        cursor.execute(query)
        otif_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return otif_data
    except Exception as e:
        print(f"Error fetching OTIF percentage: {e}")
        return None

# Route to fetch machine data
@app.route('/api/machine_data', methods=['GET'])
def get_machine_data():
    try:
        machine_data = []
        for index in range(1, 9):
            # Fetch sensor data
            data = fetch_latest_data_from_table(index)
            
            # Fetch Metal Available data
            metal_data = fetch_metal_available_data(index)
            
            if data:
                # Combine the sensor data and metal available data
                machine_info = {
                    'Sensor_No': data['Sensor_No'],
                    'Machine_No': data['Machine_No'],
                    'Level_MM': data['Level_MM'],
                    'W_Condition': data['W_Condition'],
                    'Status': data['Status'],
                    'Metal_Available_KG': metal_data['metalavailinkg'] if metal_data else None
                }
                machine_data.append(machine_info)
        
        return jsonify(machine_data)
    except Exception as e:
        print(f"Error in get_machine_data: {e}")
        return jsonify({"error": "Failed to fetch machine data"}), 500

# Route to fetch overall consumption rate
@app.route('/api/overall_consumption_rate', methods=['GET'])
def get_overall_consumption_rate():
    try:
        consumption_rate_data = fetch_overall_consumption_rate()
        return jsonify(consumption_rate_data)
    except Exception as e:
        print(f"Error in get_overall_consumption_rate: {e}")
        return jsonify({"error": "Failed to fetch overall consumption rate"}), 500

# Route to fetch molten target value
@app.route('/api/molten_target', methods=['GET'])
def get_molten_target():
    try:
        molten_target_data = fetch_molten_target()
        return jsonify(molten_target_data)
    except Exception as e:
        print(f"Error in get_molten_target: {e}")
        return jsonify({"error": "Failed to fetch molten target"}), 500

# Route to fetch total machines running
@app.route('/api/total_machines_running', methods=['GET'])
def get_total_machines_running():
    try:
        total_machines_data = fetch_total_machines_running()
        return jsonify(total_machines_data)
    except Exception as e:
        print(f"Error in get_total_machines_running: {e}")
        return jsonify({"error": "Failed to fetch total machines running"}), 500

# Route to fetch overall OTIF percentage
@app.route('/api/otif_percentage', methods=['GET'])
def get_otif_percentage():
    try:
        otif_data = fetch_otif_percentage()
        return jsonify(otif_data)
    except Exception as e:
        print(f"Error in get_otif_percentage: {e}")
        return jsonify({"error": "Failed to fetch OTIF percentage"}), 500

# Route to render index.html
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
