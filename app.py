from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
import mysql.connector

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
        query3= f""" SELECT ROUND ( ( ( SELECT SUM(change_level) * 2 FROM 
						( 	SELECT change_level 
							FROM cmr_db.S{number}_Data 
							WHERE change_level > 0 and STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
							ORDER BY S_no DESC
							LIMIT 30 ) tmp ) 
						) * (
							SELECT weight_per_mm
							FROM Material_Weight_Factor
							WHERE Sensor_No = {number} LIMIT 1 
						), 2
                    ) AS consumption_rate;
                """
        cursor.execute(query3)
        consumption_data = cursor.fetchone()
        cursor.close()

        cursor = conn.cursor(dictionary=True)
        query4 = f""" SELECT ROUND
					( ( (
						SELECT ROUND((mw.Weight_per_mm * s{number}_Data.Level_MM), 2) AS metalavailinkg
						FROM Material_Weight_Factor mw
						LEFT JOIN S{number}_Data S{number}_Data on s{number}_Data.Machine_No = mw.Machine_No
						WHERE STR_TO_DATE(s{number}_Data.Date, '%d-%m-%Y') = CURDATE()
						ORDER BY s{number}_Data.Time DESC LIMIT 1
                    ) / (
						SELECT Furnace_Depth*Weight_per_mm FROM Material_Weight_Factor WHERE Sensor_No = {number} LIMIT 1
                    ) ) * 100, 2) AS availability_per;
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
					AND W_Condition = 'Stopped';
				"""
        cursor.execute(query5)
        otif_data = cursor.fetchone()
        cursor.close()

        cursor = conn.cursor(dictionary=True)
        query6 = f""" SELECT ROUND 
					( ( (
							(SELECT Level_MM FROM S{number}_Data LIMIT 1) - 
							(SELECT Low_Level FROM Level_Limit LIMIT 1)
					) / (
							SELECT ROUND
                    ( ( (
							SELECT SUM(change_level) * 2 FROM 
							(
								SELECT `Change_Level`
								FROM `S{number}_Data`
								WHERE `Change_Level` > 0
								ORDER BY `S_no` DESC
								LIMIT 30
							) tmp
					) ) * (
							SELECT weight_per_mm
							FROM Material_Weight_Factor
							WHERE Sensor_No = {number}
					), 2 ) ) ) * 60 * (
							SELECT weight_per_mm
							FROM Material_Weight_Factor
							WHERE Sensor_No = {number}
					), 2 ) AS Refilling_Time;
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


# Route to render index.html
# @app.route('/')
# def index():
#     return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


