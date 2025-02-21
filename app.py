from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
import mysql.connector
import datetime
from datetime import datetime

app = Flask(__name__)
CORS(app)

db_config = {
    'host': '45.248.62.117',
    'user': 'vishal',
    'password': 'vishal@123',
    'database': 'cmr_db',
    'port': 3306,
    'connect_timeout': 120 
}


# Connect to the database
def get_db_connection():
    return mysql.connector.connect(**db_config)


@app.route('/api/fetch_data', methods=['GET'])
def fetch_data():
    
    data_list={}
    machine_data = []
    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)
    query = """ select consumption_rate from consumptionrateoverall """
    cursor.execute(query)
    consumption_rate_data = cursor.fetchone()
    cursor.close()

    data_list['consumption_rate_data']=consumption_rate_data

    cursor = conn.cursor(dictionary=True)
    query = """ select cntrun from view_total_machine_running """
    cursor.execute(query)
    total_machines_data = cursor.fetchone()
    cursor.close()

    data_list['total_machines_data']=total_machines_data

    cursor = conn.cursor(dictionary=True)
    query = """ SELECT ROUND(otif, 2) AS otif FROM total_otif;"""
    cursor.execute(query)
    otif_data_round = cursor.fetchone()
    cursor.close()

    data_list['otif_data_round']=otif_data_round
    
    
    for number in range(1, 9): 

        cursor = conn.cursor(dictionary=True)
        query1=f"SELECT * FROM S{number}_Data WHERE STR_TO_DATE(Date, '%d-%m-%Y') = CURDATE() ORDER BY time DESC LIMIT 1;"
        cursor.execute(query1)
        data = cursor.fetchone()
        cursor.close()
        cursor = conn.cursor(dictionary=True)

        cursor = conn.cursor(dictionary=True)
        query2= f""" SELECT ROUND((mw.Weight_per_mm * s{number}_Data.Level_MM), 2) AS metalavailinkg
					FROM Material_Weight_Factor mw
					LEFT JOIN S{number}_Data S{number}_Data on s{number}_Data.Machine_No = mw.Machine_No
					WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
					ORDER BY s{number}_Data.Time DESC LIMIT 1; 
                """
        cursor.execute(query2)
        metal_data = cursor.fetchone()
        cursor.close()

        cursor = conn.cursor(dictionary=True)
        query3= f""" SELECT 
    ROUND(
        CASE 
            WHEN 
                (SELECT Level_MM 
                 FROM cmr_db.S{number}_Data 
                 WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE() 
                 ORDER BY S_no DESC 
                 LIMIT 1) < 120
            THEN 0
            ELSE 
                (SELECT SUM(change_level) * 2
                 FROM (
                     SELECT change_level
                     FROM cmr_db.S{number}_Data
                     WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
                     ORDER BY S_no DESC
                     LIMIT 30
                 ) tmp 
                 WHERE change_level > 0) * 
                (SELECT weight_per_mm
                 FROM Material_Weight_Factor
                 WHERE Sensor_No = {number}
                 LIMIT 1)
        END, 2
    ) AS consumption_rate;
                """
        cursor.execute(query3)
        consumption_data = cursor.fetchone()
        cursor.close()

        cursor = conn.cursor(dictionary=True)
        query4 = f""" SELECT 
    CASE 
        WHEN (SELECT Level_MM 
              FROM S{number}_Data 
              ORDER BY s_no DESC 
              LIMIT 1) > 120 THEN 
            ROUND(
                ((
                    SELECT ROUND((mw.Weight_per_mm * s{number}_Data.Level_MM), 2)
                    FROM Material_Weight_Factor mw
                    LEFT JOIN S{number}_Data S{number}_Data ON s{number}_Data.Machine_No = mw.Machine_No
                    WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
                    ORDER BY s{number}_Data.Time DESC 
                    LIMIT 1
                ) / (
                    SELECT Furnace_Depth * Weight_per_mm 
                    FROM Material_Weight_Factor 
                    WHERE Sensor_No = {number} 
                    LIMIT 1
                )) * 100, 2
            )
        ELSE 0
    END AS availability_per;
                """
        cursor.execute(query4)
        availability_data = cursor.fetchone()
        cursor.close()


        cursor = conn.cursor(dictionary=True)
        query5 = f""" SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif FROM 
					(
						SELECT * 
						FROM S{number}_Data 
						ORDER BY S_no DESC LIMIT 480
					) AS tmp WHERE Level_MM < 
						(
							SELECT Low_Level 
							FROM Level_Limit 
							WHERE Sensor_No = {number}
						)
					AND W_Condition = 'Stopped' and Level_MM > 150;
				"""
        cursor.execute(query5)
        otif_data = cursor.fetchone()
        cursor.close()

        cursor = conn.cursor(dictionary=True)
        query6 = f""" SELECT 
    CASE 
        WHEN (SELECT Level_MM 
              FROM S{number}_Data 
              ORDER BY s_no DESC 
              LIMIT 1) > 120 THEN 
            IFNULL(ROUND(
                (
                    (SELECT Level_MM 
                     FROM S{number}_Data
                     ORDER BY s_no DESC
                     LIMIT 1) 
                    - (SELECT Low_Level 
                       FROM Level_Limit 
                       LIMIT 1)
                ) * 30 /
                (
                    SELECT SUM(change_level)
                    FROM (
                        SELECT Change_Level 
                        FROM S{number}_Data
                        WHERE 1 = 1
                        ORDER BY S_No DESC
                        LIMIT 30
                    ) tmp
                    WHERE change_level > 0
                ), 2), 0)
        ELSE 0
    END AS Refilling_Time;

				"""
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
    
    data_list['machine_data']=machine_data
    
    conn.close()
    
    return jsonify(data_list)


# Route to render the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the form data
        username = request.form['username']
        password = request.form['password']

        # Establish a connection to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query the users table to get the user record by username
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        # If a user record is found and password matches
        if user and user['password'] == password:
            # Check the conditions for redirection based on the fields
            if user['livedash']:
                return redirect(url_for('index'))  # Redirect to index if livedash is True
            elif user['misdash']:
                return redirect(url_for('mis'))  # Redirect to mis if misdash is True
            elif user['rawdata']:
                return redirect(url_for('rawdata'))
            else:
                return 'No valid permissions for this user.'  # Handle no permissions case
        else:
            return 'Invalid credentials. Please try again.'  # Handle invalid credentials

    # Render the login page
    return render_template('login.html')
	
# Redirect root to the login page
@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect the root URL to /login

# Route to render index.html
@app.route('/index')
def index():
    return render_template('index.html')  # Render the index page after successful login

@app.route('/mis')
def mis():
    return render_template('mis.html')  # Serve the mis.html page


@app.route('/rawdata')
def rawdata():
    return render_template('raw.html')  # Serve the mis.html page


# Route to render index.html
# @app.route('/')
# def index():
#     return render_template('index.html')


@app.route('/get_rawdata', methods=['POST'])
def get_rawdata():
    from_date = request.form['from_date']
    to_date = request.form['to_date']
    sensor_selected = request.form['sensor_number']

    print(f"From Date: {from_date}")
    print(f"To Date: {to_date}")
    print(f"Sensor Selected: {sensor_selected}")

    # Convert from_date and to_date to the desired format for the SQL query
    from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M').strftime('%m-%d-%Y %H:%M:%S')
    to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M').strftime('%m-%d-%Y %H:%M:%S')

    print(f"After change From Date: {from_date}")
    print(f"After Change To Date: {to_date}")

    # Create table name dynamically based on sensor number
    table_name = f"S{sensor_selected}_Data"

    # Query to get all data from the dynamic table
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE time BETWEEN %s AND %s
        ORDER BY time DESC;
    """

    # Open database connection and execute the query
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (from_date, to_date))
    result = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    return jsonify(result)

@app.route('/get_report', methods=['POST'])
def get_report():
    from_date = request.form['from_date']
    to_date = request.form['to_date']

    print(f"From Date before changing: {from_date}")  # Example: "02-07-2025 05:05:46"
    print(f"To Date before changing: {to_date}")  

    conn = get_db_connection()

    cursor = conn.cursor()

    consum_para = f"""
       
            SELECT TIMESTAMPDIFF(HOUR, %s, %s)
"""

    print(consum_para)
    cursor.execute(consum_para,(from_date, to_date))
    hour_factor = cursor.fetchone()

    print(hour_factor)
    


  

    # Format the from_date and to_date to mm-dd-yyyy hh:mm:ss format
    from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M').strftime('%m-%d-%Y %H:%M:%S')
    to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M').strftime('%m-%d-%Y %H:%M:%S')

    



    print(f"From Date after changing: {from_date}")  # Example: "02-07-2025 05:05:46"
    print(f"To Date after changing: {to_date}")  

    all_data = []

   

    # Loop through 8 machines (Machine 1 to Machine 8)
    for machine_id in range(1, 9):
        # Format the table name dynamically using machine_id
        table_name = f"S{machine_id}_Data"

        # Queries with dynamic table name
        sensor_query = f"""
        SELECT Sensor_No 
        FROM {table_name} 
         WHERE 
         time BETWEEN %s AND %s
        ORDER BY time DESC 
        LIMIT 1; 
        """

        machine_query = f"""
        SELECT Machine_No 
        FROM {table_name} 
        WHERE time BETWEEN %s AND %s
        ORDER BY time DESC 
        LIMIT 1;
        """

        downtime_query = f"""
              SELECT COUNT(W_condition)
        FROM {table_name}
        WHERE W_condition = 'Stopped'
        AND time BETWEEN %s AND %s;    """

      

        downtime_no_metal_query = f"""
        SELECT COUNT(W_condition) 
        FROM {table_name} 
        WHERE W_condition = 'Stopped' 
        AND Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = {machine_id})
        AND time BETWEEN %s AND %s;
        """

        consumption_rate_query = f"""
SELECT 
    ROUND(
        (
            (SELECT SUM(change_level) * 2
             FROM (
                 SELECT change_level
                 FROM {table_name} 
                 WHERE change_level > 0 
                 AND time BETWEEN %s AND %s
                 ORDER BY time DESC
             ) tmp
        )/
        (
           {hour_factor[0]}
        )
    ) * 
    (
        SELECT weight_per_mm
        FROM Material_Weight_Factor
        WHERE Sensor_No = {machine_id}
        LIMIT 1
    ), 2
) AS consumption_rate;
"""


       

        otif_query = f"""
          SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif
FROM (
    SELECT * 
    FROM {table_name} 
    WHERE time BETWEEN %s AND %s 
    ORDER BY time DESC
    LIMIT 480
) AS tmp
WHERE Level_MM < (
    SELECT Low_Level 
    FROM Level_Limit 
    WHERE Sensor_No = {machine_id}
)
AND W_Condition = 'Stopped';

        """

        # Create a cursor object to execute queries
        cursor = conn.cursor()

        # Fetch sensor number
        cursor.execute(sensor_query,(from_date, to_date))
        sensor_result = cursor.fetchone()
        sensor_number = sensor_result[0] if sensor_result else None  # Handle None result

        # Fetch machine number
        cursor.execute(machine_query,(from_date, to_date))
        machine_result = cursor.fetchone()
        machine_number = machine_result[0] if machine_result else None  # Handle None result

        # Fetch downtime minutes
        cursor.execute(downtime_query, (from_date, to_date))
        downtime_result = cursor.fetchone()
        downtime_minutes = downtime_result[0] if downtime_result else None  # Handle None result



        # Fetch downtime without metal minutes
        cursor.execute(downtime_no_metal_query, (from_date, to_date))
        downtime_no_metal_result = cursor.fetchone()
        downtime_no_metal_minutes = downtime_no_metal_result[0] if downtime_no_metal_result else None  # Handle None result

        # Fetch consumption rate
        # cursor.execute(consumption_rate_query, (from_date, to_date,from_date, to_date))
        cursor.execute(consumption_rate_query, (from_date, to_date))
        consumption_rate_result = cursor.fetchone()
        consumption_rate = consumption_rate_result[0] if consumption_rate_result else None  # Handle None result

        # Fetch OTIF value
        cursor.execute(otif_query, (from_date, to_date))
        otif_result = cursor.fetchone()
        otif = otif_result[0] if otif_result else None  # Handle None result


        # Add to data list
        machine_data = {
            'hour_factor': hour_factor,
            'sensor_number': sensor_number,
            'machine_number': machine_number,
            'downtime_minutes': downtime_minutes,
            'downtime_no_metal_minutes': downtime_no_metal_minutes,
            'consumption_rate': consumption_rate,
             'otif': otif
        }
        all_data.append(machine_data)

        # Close the cursor after each machine's queries
        cursor.close()

    # # Summary Data Queries
    # total_running_time_query = "SELECT SUM(running_time) FROM your_summary_table WHERE datetime(timestamp) BETWEEN ? AND ?"


    overall_downtime_query = """
  SELECT 
    (SELECT COUNT(W_condition)
     FROM S1_data
     WHERE W_condition = 'Stopped'
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S2_data
     WHERE W_condition = 'Stopped'
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S3_data
     WHERE W_condition = 'Stopped'
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S4_data
     WHERE W_condition = 'Stopped'
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S5_data
     WHERE W_condition = 'Stopped'
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S6_data
     WHERE W_condition = 'Stopped'
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S7_data
     WHERE W_condition = 'Stopped'
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S8_data
     WHERE W_condition = 'Stopped'
     AND time BETWEEN %s AND %s) AS total_counts;

    """

    metal_consumed_query = """

  SELECT 
    (SELECT COUNT(W_condition)
     FROM S1_data
     WHERE W_condition = 'Stopped'
     AND Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 1)
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S2_data
     WHERE W_condition = 'Stopped'
     AND Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 2)
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S3_data
     WHERE W_condition = 'Stopped'
     AND Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 3)
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S4_data
     WHERE W_condition = 'Stopped'
     AND Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 4)
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S5_data
     WHERE W_condition = 'Stopped'
     AND Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 5)
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S6_data
     WHERE W_condition = 'Stopped'
     AND Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 6)
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S7_data
     WHERE W_condition = 'Stopped'
     AND Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 7)
     AND time BETWEEN %s AND %s) +
    (SELECT COUNT(W_condition)
     FROM S8_data
     WHERE W_condition = 'Stopped'
     AND Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 8)
     AND time BETWEEN %s AND %s) AS total_count;
  
    """


    otif_summary_query = f"""
 SELECT 
    ROUND((
        (SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif
         FROM (
             SELECT * 
             FROM S1_data 
             WHERE time BETWEEN %s AND %s 
             ORDER BY time DESC
             LIMIT 480
         ) AS tmp
         WHERE Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 1)
         AND W_Condition = 'Stopped') +
        
        (SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif
         FROM (
             SELECT * 
             FROM S2_data 
             WHERE time BETWEEN %s AND %s 
             ORDER BY time DESC
             LIMIT 480
         ) AS tmp
         WHERE Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 2)
         AND W_Condition = 'Stopped') +

        (SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif
         FROM (
             SELECT * 
             FROM S3_data 
             WHERE time BETWEEN %s AND %s 
             ORDER BY time DESC
             LIMIT 480
         ) AS tmp
         WHERE Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 3)
         AND W_Condition = 'Stopped') +

        (SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif
         FROM (
             SELECT * 
             FROM S4_data 
             WHERE time BETWEEN %s AND %s 
             ORDER BY time DESC
             LIMIT 480
         ) AS tmp
         WHERE Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 4)
         AND W_Condition = 'Stopped') +

        (SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif
         FROM (
             SELECT * 
             FROM S5_data 
             WHERE time BETWEEN %s AND %s 
             ORDER BY time DESC
             LIMIT 480
         ) AS tmp
         WHERE Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 5)
         AND W_Condition = 'Stopped') +

        (SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif
         FROM (
             SELECT * 
             FROM S6_data 
             WHERE time BETWEEN %s AND %s 
             ORDER BY time DESC
             LIMIT 480
         ) AS tmp
         WHERE Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 6)
         AND W_Condition = 'Stopped') +

        (SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif
         FROM (
             SELECT * 
             FROM S7_data 
             WHERE time BETWEEN %s AND %s 
             ORDER BY time DESC
             LIMIT 480
         ) AS tmp
         WHERE Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 7)
         AND W_Condition = 'Stopped') +

        (SELECT ROUND(100 - COUNT(*) / 480.0 * 100, 2) AS otif
         FROM (
             SELECT * 
             FROM S8_data 
             WHERE time BETWEEN %s AND %s 
             ORDER BY time DESC
             LIMIT 480
         ) AS tmp
         WHERE Level_MM < (SELECT Low_Level FROM Level_Limit WHERE Sensor_No = 8)
         AND W_Condition = 'Stopped')
    ) / 8, 2) AS all_otif;


    
    """

    # Create a new cursor for summary queries
    cursor = conn.cursor()

    # cursor.execute(total_running_time_query, (from_date, to_date))
    # total_running_time = cursor.fetchone()[0]

    cursor.execute(overall_downtime_query,(from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date))
    overall_downtime = cursor.fetchone()[0]

    cursor.execute(metal_consumed_query, (from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date))
    metal_consumed = cursor.fetchone()[0]

    cursor.execute(otif_summary_query, (from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date,from_date, to_date))
    otif_summary = cursor.fetchone()[0]

    # Close the cursor
    cursor.close()

    # Close the connection
    conn.close()

    # Return the JSON response with all data and summary
    return jsonify({
        'data': all_data,
        'summary': {
        #     'total_running_time': total_running_time,
            'overall_downtime': overall_downtime,
            'metal_consumed': metal_consumed,
            'otif': otif_summary
        }
    })



if __name__ == '__main__':
    app.run(debug=True)


