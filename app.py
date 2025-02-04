# from flask import Flask, jsonify, request, render_template
# from flask_cors import CORS
# import mysql.connector
# import time
# from mysql.connector import Error
# from threading import Thread

# app = Flask(__name__)
# CORS(app)

# # Database configuration
# db_config = {
#     'host': '45.248.62.117',
#     'user': 'vishal',
#     'password': 'vishal@123',
#     'database': 'cmr_db',
#     'port': 3306
# }

# MAX_RETRIES = 3
# RETRY_DELAY = 5  # seconds

# # Function to get a database connection with retries
# def get_db_connection_with_retry():
#     attempts = 0
#     while attempts < MAX_RETRIES:
#         try:
#             conn = mysql.connector.connect(**db_config)
#             if conn.is_connected():
#                 return conn
#         except Error as e:
#             attempts += 1
#             print(f"Attempt {attempts}/{MAX_RETRIES} failed to connect to the database: {e}")
#             if attempts < MAX_RETRIES:
#                 time.sleep(RETRY_DELAY)  # Wait before retrying
#             else:
#                 raise Exception("Max retries reached. Could not connect to the database.")
#     return None  # If all retries fail

# # Function to fetch the latest data from the specific table
# def fetch_latest_data_from_table(number):
#     conn = get_db_connection_with_retry()
#     if conn is None:
#         return {'Sensor Number': 'N/A', 'Machine Number': 'N/A', 'Current Level(MM)': 'N/A'}

#     cursor = conn.cursor(dictionary=True)
#     query = f"SELECT * FROM S{number}_Data WHERE STR_TO_DATE(Date, '%d-%m-%Y') = CURDATE() ORDER BY time DESC LIMIT 1;"
#     cursor.execute(query)
#     latest_data = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return latest_data if latest_data else {'Sensor Number': 'N/A', 'Machine Number': 'N/A', 'Current Level(MM)': 'N/A'}

# # Function to fetch Metal Available (KG) from Material_Weight_Factor
# def fetch_metal_available_data(number):
#     conn = get_db_connection_with_retry()
#     if conn is None:
#         return {'metalavailinkg': 'N/A'}

#     cursor = conn.cursor(dictionary=True)
#     query = f"""
#     SELECT 
#         ROUND((mw.Weight_per_mm * s{number}_Data.Level_MM), 2) AS metalavailinkg
#     FROM Material_Weight_Factor mw
#     LEFT JOIN S{number}_Data S{number}_Data on s{number}_Data.Machine_No = mw.Machine_No
#     WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
#     ORDER BY s{number}_Data.Time DESC
#     LIMIT 1;
#     """
#     cursor.execute(query)
#     metal_data = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return metal_data if metal_data else {'metalavailinkg': 'N/A'}

# # Function to fetch consumption rate from Material_Weight_Factor
# def fetch_consumption_rate_data(number):
#     conn = get_db_connection_with_retry()
#     if conn is None:
#         return {'consumption_rate': 'N/A'}

#     cursor = conn.cursor(dictionary=True)
#     query = f"""
#    SELECT 
#     ROUND(
#         (
#             (SELECT SUM(change_level) * 2
#              FROM (
#                  SELECT change_level
#                  FROM cmr_db.S{number}_Data 
#                    WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
#                  ORDER BY time DESC
#                  LIMIT 30
#              ) tmp
#             ) ) * 
#             (
#                 SELECT weight_per_mm
#                 FROM Material_Weight_Factor
#                 WHERE Sensor_No = {number}
#                 LIMIT 1
#             ), 2
#     ) AS consumption_rate;
#     """
#     cursor.execute(query)
#     consumption_data = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return consumption_data if consumption_data else {'consumption_rate': 'N/A'}

# # Query for Availability%
# def fetch_availability_per_data(number):
#     conn = get_db_connection_with_retry()
#     if conn is None:
#         return {'availability_per': 'N/A'}

#     cursor = conn.cursor(dictionary=True)
#     query = f"""
# SELECT 
#   (SELECT Level_MM FROM S{number}_Data LIMIT 1) / 
#   (SELECT Furnace_Depth FROM Material_Weight_Factor WHERE Sensor_No = {number} LIMIT 1) AS availability_per;
#     """
#     cursor.execute(query)
#     availability_data = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return availability_data if availability_data else {'availability_per': 'N/A'}

# # Query for OTIF%
# def fetch_otif_per_data(number):
#     conn = get_db_connection_with_retry()
#     if conn is None:
#         return {'otif': 'N/A'}

#     cursor = conn.cursor(dictionary=True)
#     query = f"""
# SELECT COUNT(*) AS otif
# FROM (
#     SELECT * 
#     FROM S{number}_Data 
#     ORDER BY time DESC
#     LIMIT 480
# ) AS tmp
# WHERE Level_MM < (
#     SELECT Low_Level 
#     FROM Level_Limit 
#     WHERE Sensor_No = {number}
# )
# AND W_Condition = 'Stopped';
#     """
#     cursor.execute(query)
#     otif_data = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return otif_data if otif_data else {'otif': 'N/A'}

# # Query for Refilling Time
# def fetch_RefillingTime_data(number):
#     conn = get_db_connection_with_retry()
#     if conn is None:
#         return {'Refilling_Time': 'N/A'}

#     cursor = conn.cursor(dictionary=True)
#     query = f"""
#   SELECT 
#     ROUND(
#         (
#             (SELECT SUM(change_level) * 3
#              FROM (
#                  SELECT change_level
#                  FROM cmr_db.S{number}_Data 
#                    WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
#                  ORDER BY time DESC
#                  LIMIT 100
#              ) tmp
#             ) ) * 
#             (
#                 SELECT weight_per_mm
#                 FROM Material_Weight_Factor
#                 WHERE Sensor_No = {number}
#                 LIMIT 1
#             ), 2
#     ) AS Refilling_Time;
#     """
#     cursor.execute(query)
#     refilling_data = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return refilling_data if refilling_data else {'Refilling_Time': 'N/A'}

# # Function to fetch machine data concurrently
# def fetch_machine_data(index, result_list):
#     result_list[index] = {
#         'data': fetch_latest_data_from_table(index),
#         'metal_data': fetch_metal_available_data(index),
#         'consumption_data': fetch_consumption_rate_data(index),
#         'availability_data': fetch_availability_per_data(index),
#         'otif_data': fetch_otif_per_data(index),
#         'refilling_data': fetch_RefillingTime_data(index),
#     }

# @app.route('/api/machine_data', methods=['GET'])
# def get_machine_data():
#     try:
#         machine_data = []
#         threads = []
#         results = {}

#         # Fetch data for all machines concurrently using threads
#         for index in range(1, 9):
#             thread = Thread(target=fetch_machine_data, args=(index, results))
#             threads.append(thread)
#             thread.start()

#         # Wait for all threads to finish
#         for thread in threads:
#             thread.join()

#         # Collect results after all threads have finished
#         for index in range(1, 9):
#             machine_data.append({
#                 'index': index,
#                 'data': results[index]['data'],
#                 'metal_data': results[index]['metal_data'],
#                 'consumption_data': results[index]['consumption_data'],
#                 'availability_data': results[index]['availability_data'],
#                 'otif_data': results[index]['otif_data'],
#                 'refilling_data': results[index]['refilling_data']
#             })

#         return jsonify(machine_data)
#     except Exception as e:
#         return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# # Route to render index.html
# @app.route('/')
# def index():
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)

# --------------------------------------------------------------------------------



from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
import time
import threading

app = Flask(__name__)
CORS(app)

# Database configuration
# db_config = {
#     'host': '127.0.0.1',
#     'user': 'root',
#     'password': 'root@1234',
#     'database': 'cmr_db',
#     'port': 3306
# }

db_config = {
    'host': '45.248.62.117',
    'user': 'vishal',
    'password': 'vishal@123',
    'database': 'cmr_db',
    'port': 3306
}


# Connect to the database
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to fetch latest data from a specific table
def fetch_latest_data_from_table(number):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # query = f"SELECT * FROM S{number}_Data WHERE Date = CurDate() ORDER BY time DESC LIMIT 1;"

    

    query = f"SELECT * FROM S{number}_Data WHERE STR_TO_DATE(Date, '%d-%m-%Y') = CURDATE() ORDER BY time DESC LIMIT 1;"


    cursor.execute(query)
    latest_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return latest_data

# Function to fetch Metal Available (KG) from Material_Weight_Factor
def fetch_metal_available_data(number):
    conn = get_db_connection()
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

#03.02.2025 --15:04 PM
    # Function to fetch consumption rate from Material_Weight_Factor
def fetch_consumption_rate_data(number):
    conn = get_db_connection()
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

##-------------


##Query for Availability% --03-02-2025
def fetch_availability_per_data(number):
    conn = get_db_connection()
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


##Query for Otif% --04-02-2025
def fetch_otif_per_data(number):
    conn = get_db_connection()
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

##Query for Refilling Time --04-02-2025
def fetch_RefillingTime_data(number):
    conn = get_db_connection()
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




# Function to fetch data for Overall Consumption Rate
def fetch_overall_consumption_rate():
    # Add your query logic for Overall Consumption Rate (Q1) here
    conn = get_db_connection()
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

# Function to fetch Molten Metal Target (Plant)
def fetch_molten_target():
    conn = get_db_connection()
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

# Function to fetch Total Machines Running (to be updated)
def fetch_total_machines_running():
    # Add your query logic for Total Machines Running here
    conn = get_db_connection()
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

# Function to fetch Overall OTIF % (to be updated)
def fetch_otif_percentage():
    # Add your query logic for Overall OTIF % here
    conn = get_db_connection()
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

    

# Route to fetch machine data
@app.route('/api/machine_data', methods=['GET'])
def get_machine_data():
    machine_data = []
    conn = get_db_connection()
    
    for number in range(1, 9):  
        
        cursor = conn.cursor(dictionary=True)
        query1=f"SELECT * FROM S{number}_Data WHERE STR_TO_DATE(Date, '%d-%m-%Y') = CURDATE() ORDER BY time DESC LIMIT 1;"

        # Fetch sensor data
        cursor.execute(query1)
        data = cursor.fetchone()
        cursor.close()
        # Fetch Metal Available data
        cursor = conn.cursor(dictionary=True)
        query2= f"""
            SELECT 
                ROUND((mw.Weight_per_mm * s{number}_Data.Level_MM), 2) AS metalavailinkg
            FROM Material_Weight_Factor mw
            LEFT JOIN S{number}_Data S{number}_Data on s{number}_Data.Machine_No = mw.Machine_No
            WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
            ORDER BY s{number}_Data.Time DESC
            LIMIT 1;
            """
        # Fetch sensor data
        cursor.execute(query2)
        metal_data = cursor.fetchone()
        cursor.close()
        
        cursor = conn.cursor(dictionary=True)
        query3=f"""
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


        # Fetch sensor data
        cursor.execute(query3)
        consumption_data = cursor.fetchone()
        cursor.close()

        cursor = conn.cursor(dictionary=True)
        query4 = f"""
            SELECT 
            (SELECT Level_MM FROM S{number}_Data LIMIT 1) / 
            (SELECT Furnace_Depth FROM Material_Weight_Factor WHERE Sensor_No = {number} LIMIT 1) AS availability_per;

                """
        # Fetch sensor data
        cursor.execute(query4)
        availability_data = cursor.fetchone()
        cursor.close()


        cursor = conn.cursor(dictionary=True)
        query5 = f"""
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
        # Fetch sensor data
        cursor.execute(query5)
        otif_data = cursor.fetchone()
        cursor.close()

        cursor = conn.cursor(dictionary=True)
        query6 = f"""
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
        # Fetch sensor data
        cursor.execute(query6)
        refilling_data = cursor.fetchone()
        cursor.close()
        
        if data:
            # Combine the sensor data and metal available data
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
        
    conn.close()
    
    return jsonify(machine_data)


# Route to fetch overall consumption rate
@app.route('/api/overall_consumption_rate', methods=['GET'])
def get_overall_consumption_rate():
    consumption_rate_data = fetch_overall_consumption_rate()
    return jsonify(consumption_rate_data)  # Return the result as JSON

# Route to fetch molten target value
@app.route('/api/molten_target', methods=['GET'])
def get_molten_target():
    molten_target_data = fetch_molten_target()
    return jsonify(molten_target_data)  # Return the result as JSON

# Route to fetch total machines running
@app.route('/api/total_machines_running', methods=['GET'])
def get_total_machines_running():
    total_machines_data = fetch_total_machines_running()
    return jsonify(total_machines_data)  # Return the result as JSON

# Route to fetch overall OTIF percentage
@app.route('/api/otif_percentage', methods=['GET'])
def get_otif_percentage():
    otif_data = fetch_otif_percentage()
    return jsonify(otif_data)  # Return the result as JSON

# Route to render index.html
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


