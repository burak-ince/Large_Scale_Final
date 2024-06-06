from flask import render_template, request, jsonify, redirect, url_for,session
from app import app
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from uuid import uuid4
from app.flightdb import conn
from app.queue import addMessagetoQueue

@app.route('/v1/change',methods =['GET'])
def home():
    return jsonify("Changes Applied6"),200

@app.route('/v1/admin_login',methods = ['POST'])
def admin_login():
    try:
        form_data = request.json

        username = form_data.get('username')
        password = form_data.get('password')
        print(username,password)
        connection = conn()
        cur = connection.cursor()
        sql_query = """
            SELECT * FROM admintable
            WHERE username = %s
            AND password = %s
        """

        cur.execute(sql_query,(username,password))

        user = cur.fetchone()
        print(user)
        cur.close()
        connection.close()

        if user:
            response_data = {"status":"TRUE"}
        else:
            response_data = {"status":"FALSE"}
        
        return jsonify(response_data),200

    except Exception as e:
        error_message = str(e)
        response_data = {"status": "error", "message": error_message}
        return jsonify(response_data), 400


@app.route('/v1/admin_signup',methods = ['POST'])
def admin_signup():
    try:
        form_data = request.json

        username = form_data.get('username')
        password = form_data.get('password')

        connection = conn()
        cur = connection.cursor()

        cur.execute("SELECT * FROM admintable WHERE USERNAME = %s",(username,))

        data = cur.fetchone()
        if data is None:
            cur.execute("INSERT INTO admintable (username,password) VALUES (%s,%s)",(username,password,))
            message = {"status":"TRUE"}
        else:
            message = {"status":"FALSE"}
        connection.commit()
        cur.close()
        connection.close()
        
        return jsonify(message),200

    except Exception as e:
        error_message = str(e)
        response_data = {"status": "error", "message": error_message}
        return jsonify(response_data), 400


@app.route('/v1/add_flight', methods = ['POST'])
def add_flight():
    try:
        form_data = request.json

        departure_airport = form_data.get('departure_airport')
        arrival_airport = form_data.get('arrival_airport')
        ucus_tarihi = form_data.get('ucus_tarihi')
        ucus_kodu = int(form_data.get('ucus_kodu'))
        kapasite = int(form_data.get('kapasite'))
        mil = int(form_data.get('mil'))
        direct_flight = form_data.get('direct_flight')
        flexible_date = form_data.get('flexible_dates')

        # Save it to the database
        connection = conn()
        cur = connection.cursor()
        
        cur.execute("SELECT * FROM flights WHERE flight_code = %s",(ucus_kodu,))

        existing_flight = cur.fetchone()

        if existing_flight:
            response_data = {"status" : "FALSE","message":"Flight code already exists."}
        
        else:
            cur.execute(
                "INSERT INTO flights (departure_airport, arrival_airport, departure_date, flight_code, passengers, mil, flexible_dates, direct_flight) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (departure_airport, arrival_airport, ucus_tarihi, ucus_kodu, kapasite, mil, flexible_date, direct_flight)
            )

            # Commit the transaction and close the connection
            connection.commit()
            response_data = {"status":"TRUE"}
        cur.close()
        connection.close()
        
        return jsonify(response_data),200

    except Exception as e:
        error_message = str(e)
        response_data = {"status": "error", "message": error_message}
        return jsonify(response_data), 400
    

@app.route('/v1/search_flight',methods = ['POST'])
def search_flight():
    try:
        form_data = request.json

        departure_airport = form_data.get('departure_airport')
        arrival_airport = form_data.get('arrival_airport')
        ucus_tarihi = form_data.get('departure_date')
        passenger_count = int(form_data.get('passengers'))
        direct_flight = form_data.get('direct_flight')
        flexible_date = form_data.get('flexible_dates')

        sql_query = """
            SELECT * FROM flights
            WHERE departure_airport = %s
            AND arrival_airport = %s
            AND departure_date = %s
            AND passengers > %s
            AND direct_flight = %s
            AND flexible_dates = %s
        """
        connection = conn()
        cur = connection.cursor()

        cur.execute(sql_query, (departure_airport, arrival_airport, ucus_tarihi, passenger_count, direct_flight, flexible_date,))
        rows = cur.fetchall()
        connection.close()

        if rows:
            response_data = {"status":"TRUE","flight_list":rows}
        else:
            response_data = {"status":"FALSE"}

        return jsonify(response_data),200
    except Exception as e:
        error_message = str(e)
        response_data = {"status": "error", "message": error_message}
        return jsonify(response_data), 400

@app.route('/v1/buy_ticket', methods = ['POST'])
def buy_ticket():
    try:
        form_data = request.json

        name = form_data.get('name')
        surname = form_data.get('surname')
        email = form_data.get('email')
        date = form_data.get('date')
        passenger_count = int(form_data.get('passengers'))
        milesandsmiles = form_data.get('milesandsmiles')
        flight_id = form_data.get('selected_flight_id')

        connection = conn()

        cur = connection.cursor()


        if milesandsmiles == 'on':
            # create a new milesandsmiles user with name surname and date and mile= 0
            cur.execute("""
                CREATE TABLE IF NOT EXISTS milesandsmilesuser (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    surname VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    mile INT NOT NULL,
                    CONSTRAINT unique_name UNIQUE (name)
                )
            """)

            # Insert the user's information into the milesandsmilesuser table
            # Give 200 miles as gift for new user.
            cur.execute("""
                INSERT INTO milesandsmilesuser (name, surname, email, date, mile)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, surname, email, date, 200))

            queue_message = {"email":email}

            addMessagetoQueue(queue_message)

            # Commit the transaction
            connection.commit()

            response_data = {"status":"TRUE","message":"User Created!"}


        cur.execute("""
            UPDATE flights
            SET passengers = passengers - %s
            WHERE id = %s
        """, (passenger_count, flight_id))
        
        connection.commit()

        cur.close()
        connection.close()

        response_data = {"status":"TRUE"}
        return jsonify(response_data),200
    except Exception as e:
        error_message = str(e)
        response_data = {"status": "error", "message": error_message}
        return jsonify(response_data), 400
    
@app.route('/v1/mileslogin', methods = ['POST'])
def miles_login():
    try:
        form_data = request.json

        username = form_data.get('name')
        password = form_data.get('surname')

        connection = conn()
        cur = connection.cursor()

        # Execute a SELECT query to check if the username and password match
        cur.execute("""
            SELECT * FROM milesandsmilesuser
            WHERE name = %s AND surname = %s
        """, (username, password))

        # Fetch the result of the query
        user_data = cur.fetchone()

        # Close the cursor and connection
        cur.close()
        connection.close()

        if user_data:
            # Username and password match
            # Perform further actions or return a success response
            return jsonify({"status": "TRUE", "message": "Login successful","user_data":user_data})
        else:
            # Username and password do not match
            # Return an error response
            return jsonify({"status": "FALSE", "message": "Invalid username or password"}), 200
        
    except Exception as e:
        # Handle any exceptions that occur during the process
        error_message = str(e)
        return jsonify({"status": "error", "message": error_message}), 500

@app.route('/v1/milesbuyticket',methods =['POST'])
def miles_buy_ticket():
    try:
        form_data = request.json

        user_id = form_data.get('milesuserid')
        passenger_count = form_data.get('passengers')
        flight_id = form_data.get('selected_flight_id')

        connection = conn()
        cur = connection.cursor()

        cur.execute("SELECT mile FROM milesandsmilesuser WHERE id = %s", (user_id,))

        user_miles = cur.fetchone()
        user_miles = user_miles[0]

        cur.execute("SELECT mil, passengers FROM flights WHERE id = %s", (flight_id,))
        flight_data = cur.fetchone()
        
        flight_miles, current_passenger_count = flight_data

        if int(user_miles) >= int(flight_miles):
            # Update the user's mile points and the flight's passenger count
            new_user_miles = int(user_miles) - int(flight_miles)
            new_passenger_count = int(current_passenger_count) - int(passenger_count)

            cur.execute("UPDATE milesandsmilesuser SET mile = %s WHERE id = %s", (new_user_miles, user_id))
            cur.execute("UPDATE flights SET passengers = %s WHERE id = %s", (new_passenger_count, flight_id))

            message = "You have used miles! Congrat"
            
        else:
            # No need to apply scheduler for updating miles
            # It will update flighted_miles/3 + current_miles
            # If the flight cancelled, mile transactions will be taken back
            new_passenger_count = int(current_passenger_count) - int(passenger_count)
            new_user_miles = int(user_miles) + int(flight_miles/3)
            cur.execute("UPDATE milesandsmilesuser SET mile = %s WHERE id = %s", (new_user_miles, user_id))
            cur.execute("UPDATE flights SET passengers = %s WHERE id = %s", (new_passenger_count, flight_id))
            message = "You don't have enough miles! Use your credit card!"
        
        connection.commit()
        cur.close()
        connection.close()

        return jsonify({"status":"TRUE","message":message}),200


    except Exception as e:
        # Handle any exceptions that occur during the process
        error_message = str(e)
        return jsonify({"status": "error", "message": error_message}), 500
