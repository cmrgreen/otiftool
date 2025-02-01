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

# Routes to handle the API calls
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

# Other routes with similar try-except blocks...

if __name__ == '__main__':
    app.run(debug=True)
