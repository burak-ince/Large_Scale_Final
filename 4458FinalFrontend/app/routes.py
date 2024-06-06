from flask import render_template, request, jsonify, redirect, url_for,session
from app import app
import requests

app.secret_key = 'random_secret'

@app.route('/v1',methods = ['GET'])
def home():
    return render_template('index.html')

@app.route('/v1/admin_login',methods = ['GET','POST'])
def admin_login():
    if request.method == 'GET':
        return render_template("adminlogin.html")
    else:
        login_data = request.form.to_dict()

        response = requests.post("https://finalapigateway.azure-api.net/v1/admin_login",json=login_data)

        api_response = response.json()
        status = api_response.get('status')
        if status == 'TRUE':
            try:
                session['logged_in'] = True
                return redirect(url_for('add_flight'))
            except requests.exceptions.JSONDecodeError:
                # Handle the case where the response is not JSON
                return "Invalid response format. Could not decode JSON."
        else:
            # Handle unexpected status codes
            return render_template("adminlogin.html",message="Wrong Credentials")

@app.route('/v1/admin_signup',methods = ['GET','POST'])
def admin_signup():
    if request.method == 'GET':
        return render_template("adminsignup.html")
    else:
        login_data = request.form.to_dict()

        response = requests.post("https://finalapigateway.azure-api.net/v1/admin_signup",json=login_data)

        api_response = response.json()
        status = api_response.get('status')
        print(status)
        if status == 'TRUE':
            session['logged_in'] = True
            return redirect(url_for('add_flight'))
        else:
            message = "User exists"
            return render_template("adminsignup.html",message = message)

@app.route('/v1/add_flight',methods =['GET','POST'])
def add_flight():
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'GET':
            return render_template("addflight.html")
        else:
            flight_data = request.form.to_dict()
            
            response = requests.post("https://finalapigateway.azure-api.net/v1/add_flight", json = flight_data)

            api_response = response.json()

            status = api_response.get('status')

            if status == 'TRUE':
                api_response = response.json()
                return render_template("addflight.html",message = "Flight Created!")
            else:
                message = api_response.get('message')
    
                return render_template("addflight.html",message = message)
    else:
        return redirect(url_for('admin_login'))
        
@app.route('/v1/search_flight', methods=['GET', 'POST'])
def search_flight():
    if request.method == 'GET':
        return render_template("searchflight.html")
    else:
        flight_data = request.form.to_dict()

        response = requests.post("https://finalapigateway.azure-api.net/v1/search_flight",json=flight_data)

        api_response = response.json()

        status = api_response.get('status')

        if status == 'TRUE':
            flight_list = api_response.get('flight_list')
            
            session['flight_list'] = flight_list

            return redirect(url_for('select_flight'))
        else:
            # Redirect to the search page again
            return render_template("searchflight.html",message = "Sorry, Flight not found!")

@app.route('/v1/select_flight', methods=['GET','POST'])
def select_flight():
    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        per_page = 5    
        flight_list = session.get('flight_list')
        total_flights = len(flight_list)
        total_pages = (total_flights + per_page - 1) // per_page

        start = (page - 1) * per_page
        end = start + per_page
        paginated_flight_list = flight_list[start:end]

        return render_template("selectflight.html", 
                               flight_list=paginated_flight_list, 
                               page=page, 
                               total_pages=total_pages)
    else:
        selected_flight_data_str = request.form['selected_flight']
        session['selected_flight_id'] = selected_flight_data_str
        return redirect(url_for('buy_ticket'))

@app.route('/v1/buy_ticket', methods=['POST','GET'])
def buy_ticket():
    if request.method == 'GET':
        try:
            # Retrieve the selected flight data from the form submission
            selected_flight_id = session.get('selected_flight_id')
            flight_list = session['flight_list']
            miles_user = session.get('miles_user')

            for flight in flight_list:
                if flight[0] == int(selected_flight_id):
                    selected_flight=flight
                    session['selected_flight'] = selected_flight

            if miles_user:
                user_data = session.get('user_data')
                print(user_data)
                return render_template("buyticket.html",selected_flight=selected_flight,user_data=user_data)
            else:
                return render_template("buyticket.html",selected_flight=selected_flight)

        except Exception as e:
            return jsonify(status="error", message=str(e)), 400
    
    else:
        user_data = request.form.to_dict()
        selected_flight_id = session.get('selected_flight_id')
        user_data['selected_flight_id'] = selected_flight_id
        response = requests.post("https://finalapigateway.azure-api.net/v1/buy_ticket",json=user_data)

        api_response = response.json()

        status = api_response.get('status')
        message = api_response.get('message')
        print(api_response)
        if message:
            print(message)
        if status == 'TRUE':
            return render_template('index.html',message='Ticket Created')

@app.route('/v1/mileslogin',methods= ['GET','POST'])
def login_milesandsmiles():
    if request.method == 'GET':
        return render_template("mileslogin.html")
    else:
        miles_user_data = request.form.to_dict()

        response = requests.post("https://finalapigateway.azure-api.net/v1/mileslogin",json=miles_user_data)
        print(response)
        api_response = response.json()

        status = api_response.get('status')
        user_data = api_response.get('user_data')
        if status == 'TRUE':
            session['miles_user'] = True
            session['user_data'] = user_data
            return redirect(url_for('miles_buy_ticket'))
        
        else:
            message = 'Wrong Credentials'
            return render_template("mileslogin.html",message=message)

@app.route('/v1/milesbuyticket',methods=['GET','POST'])
def miles_buy_ticket():
    selected_flight_id = session.get('selected_flight_id')
    flight_list = session['flight_list']
    user_data = session.get('user_data')
    if request.method == 'GET':
        for flight in flight_list:
                if flight[0] == int(selected_flight_id):
                    selected_flight=flight
                    session['selected_flight'] = selected_flight

        return render_template("milesuserbuyticket.html",selected_flight= selected_flight,user_data=user_data)
    else:
        form_data = request.form.to_dict()
        request_data = {"milesuserid" : user_data[0],"passengers": form_data.get('passengers'),"selected_flight_id":selected_flight_id}
        print(request_data)
        response = requests.post("https://finalapigateway.azure-api.net/v1/milesbuyticket",json=request_data)

        api_response = response.json()
        print(api_response)
        status = api_response.get('status')

        if status == 'TRUE':
            message = api_response.get('message')
            return render_template('index.html',message =message)