from flask import Blueprint, render_template, request, session, url_for, redirect, flash
from database import conn
from datetime import datetime
from login_required import staff_login_required


staff = Blueprint('staff', __name__)

@staff.route('/staffHome')
@staff_login_required
def staffHome():
        
    #fetch data from session
    username = session["username"]
    cursor = conn.cursor()
    query = 'SELECT first_name, last_name, airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone() 
    cursor.close()
    #debugging
    print(data["first_name"], data["last_name"], data["airline_name"])
    cursor.close()
    return render_template("staffHome.html",username = username, info = data)

@staff.route('/flightManage', methods = ['GET', 'POST'])
@staff_login_required
def viewFlight():

    #get airline name
    airline_name = session['airline_name']
    default = ""
    if request.method == "POST": 
        #grabs information from the forms
        dept_from = request.form['dept_from']
        arr_at = request.form['arr_at']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
            return render_template("flightManage.html", error = "The dates you entered are invalid.")

        #database query
        cursor = conn.cursor()
        query = "SELECT * FROM flight NATURAL JOIN airplane, airport as A, airport as B \
        where airline_name = %s AND date(dept_time) >= %s AND date(dept_time) <= %s \
        AND flight.dept_from = A.name and flight.arr_at = B.name and (A.name = %s or A.city = %s) \
            and (B.name = %s or B.city = %s)"
        cursor.execute(query, (airline_name, start_date, end_date, dept_from, dept_from, arr_at, arr_at))
        data1 = cursor.fetchall() 
        cursor.close()
        msg = (dept_from, arr_at, start_date, end_date)

    else: 
        # default views 
        cursor = conn.cursor()
        query = 'SELECT * FROM flight WHERE airline_name = %s AND DATE(dept_time) BETWEEN DATE(CURRENT_TIMESTAMP) \
        AND DATE(CURRENT_TIMESTAMP) + INTERVAL 30 DAY'
        cursor.execute(query, (airline_name))
        data1 = cursor.fetchall() 
        cursor.close()
        default = "Default: Future 30 Days"
        msg = "Default: Future 30 Days"

    # send to the html   
    if data1:
        for each in data1:
            print("Received Data:/n", each['airline_name'],each['flight_num'],each['dept_time'])
            return render_template('flightManage.html', flights=data1, msg = msg)
    else: 
        #returns an error message to the html page
        noFound = "No flights available within the given conditions"
        return render_template('flightManage.html', default = default, noFound = noFound)


@staff.route('/addFlight', methods = ['GET', 'POST'])
@staff_login_required
def add_flight():
    #get airline name
    airline_name = session['airline_name']

    if request.method == "POST":
        #grabs information from the forms
        flight_num = request.form['flight_num1']
        dept_time = request.form['dept_time1']
        arr_time = request.form['arr_time1']
        base_price = float(request.form['base_price1'])
        flight_status = "on time"
        dept_from = request.form['dept_from1']
        arr_at = request.form['arr_at1']
        airplane_id = request.form['airplane_id1']
        print(dept_time)
        if datetime.strptime(dept_time, "%Y-%m-%dT%H:%M:%S") > datetime.strptime(arr_time, "%Y-%m-%dT%H:%M:%S"):
            return render_template("flightManage.html", error = "The dates you entered are invalid.")

        cursor = conn.cursor()
        
        #check foreign_key constraint and duplicate
        #airplane 
        query = "SELECT airplane_id FROM airplane"
        cursor.execute(query)
        data = cursor.fetchall()
        airplane_list = []
        for line in data:
            airplane_list.append(line["airplane_id"])
        if airplane_id not in airplane_list: 
            noFound = "Airplane ID Not Found"
            return render_template('flightManage.html', noFound = noFound)
        #airport
        query = "SELECT name FROM airport"
        cursor.execute(query)
        data = cursor.fetchall()
        airport_list = []
        for line in data:
            airport_list.append(line["name"])
        if dept_from not in airport_list or arr_at not in airport_list:
            noFound = "Airport Not Found"
            return render_template('flightManage.html', noFound = noFound)


        query = "SELECT * FROM flight WHERE (airline_name, flight_num, dept_time) = (%s, %s, %s)"
        cursor.execute(query, (airline_name, flight_num, dept_time))
        data = cursor.fetchall()
        if data: 
            noFound = "Flight Already Exist"
            return render_template('flightManage.html', noFound = noFound)
        
        #update database
        query = "INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (airline_name, flight_num, dept_time, arr_time,\
            base_price, flight_status, dept_from, arr_at, airplane_id))
        msg = "Add Flights Success"
        print(msg)
        cursor.close()
        conn.commit()
        session["flight_created"] = True
        return redirect("/flightManage")
    else: 
        render_template("flightManage.html")

@staff.route('/updateFlight/<string:flight_num>/<string:dept_time>', methods = ['GET', 'POST'])
@staff_login_required
def updateFlight(flight_num, dept_time): 

    #get airline name
    airline_name = session['airline_name']

    if request.method == "POST": 
        #fetch selection 
        new_status = request.form.get('statusSelect')
        print("new-status", new_status)
        #update database
        cursor = conn.cursor()
        query = "UPDATE flight SET flight_status = %s WHERE (airline_name, flight_num, dept_time) = (%s, %s, %s)"
        cursor.execute(query, (new_status, airline_name, flight_num, dept_time))
        cursor.close()
        conn.commit()
        message = "Update Flights Success"
        session["flight_updated"] = True
        return redirect("/flightManage")
    else: 
        cursor = conn.cursor()
        #check if such flight exits
        query = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND dept_time = %s"
        cursor.execute(query, (airline_name, flight_num, dept_time))
        data = cursor.fetchone()
        cursor.close()
        if data: 
            print(data)
            return render_template("updateFlight.html", flight = data)
        else: 
            noFound = "There's an issue in updating the flight: such flight does not exist"
            return render_template('flightManage.html', noFound = noFound)

@staff.route('/viewPassengers/<string:flight_num>/<string:dept_time>')
@staff_login_required
def viewPassenger(flight_num, dept_time):
    #get airline name
    airline_name = session['airline_name']
    print(flight_num, dept_time)
    cursor = conn.cursor()
    #check if such flight exits
    query = "SELECT flight_num, dept_time, email, name, purchase_time FROM ticket \
        JOIN customer ON ticket.cust_email = customer.email WHERE (airline_name, flight_num, dept_time) = (%s, %s, %s)"
    cursor.execute(query, (airline_name, flight_num, dept_time))
    data = cursor.fetchall()
    cursor.close()
    print("data: 1", data)
    if data: 
        for each in data:
            print("data:", each)
        return render_template("viewPassengers.html", passenger = data)
    else: 
        noFound = "This flight has no passengers yet"
        return render_template('viewPassengers.html', noFound = noFound)


@staff.route('/airSystemManage/airplane', methods = ['GET', 'POST'])
@staff_login_required
def managePlane():
    #get airline name
    airline_name = session['airline_name']

    if request.method == "POST":
        #fetch data
        airplane_id = request.form["airplane_id"]
        seats = request.form["seats"]

        #check duplicates
        cursor = conn.cursor()
        query = "SELECT * FROM airplane WHERE (airline_name, airplane_id) = (%s, %s)"
        cursor.execute(query, (airline_name, airplane_id))
        data = cursor.fetchall()
        if data: 
            noFound = "Such airplane ID already exists"
            return render_template("airSystemManage.html", noFound = noFound, message = "airplane", state_plane = True)
        cursor.close()

        #initiate query
        cursor = conn.cursor()
        query = "INSERT INTO airplane VALUES (%s, %s, %s)"
        cursor.execute(query,(airline_name,airplane_id,seats))
        cursor.close()
        conn.commit()
        session["airplane_updated"] = True
        return redirect("/airSystemManage/airplane")

    else: 
        # display all the planes operated by the airline
        cursor = conn.cursor()
        query = "SELECT * FROM airplane WHERE airline_name = %s"
        cursor.execute(query,(airline_name))
        data = cursor.fetchall()
        cursor.close()
        if data: 
            for each in data:
                print("data:", each)
            return render_template("airSystemManage.html", airplane = data, state_plane = True)
        else: 
            noFound = "There is not airplane in the system"
            return render_template("airSystemManage.html", noFound = noFound, state_plane = True)


@staff.route('/airSystemManage/airport', methods = ['GET', 'POST'])
@staff_login_required
def manageAirport():
    if request.method == "POST":
        #fetch data
        name = request.form["name"]
        city = request.form["city"]

        #check duplicates
        cursor = conn.cursor()
        query = "SELECT * FROM airport WHERE name = %s"
        cursor.execute(query, (name))
        data = cursor.fetchall()
        if data: 
            noFound = "Such airport name already exists"
            return render_template("airSystemManage.html", noFound = noFound, message = "airport", state_airport = True)
        cursor.close()

        #initiate query
        cursor = conn.cursor()
        query = "INSERT INTO airport VALUES (%s, %s)"
        cursor.execute(query,(name,city))
        cursor.close()
        conn.commit()
        session["airport_updated"] = True
        return redirect("/airSystemManage/airport")

    else: 
        # display all the planes operated by the airline
        cursor = conn.cursor()
        query = "SELECT * FROM airport"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        if data: 
            for each in data:
                print("data:", each)
            return render_template("airSystemManage.html", airport = data, state_airport = True)
        else: 
            noFound = "There is no airport in the system"
            return render_template("airSystemManage.html", noFound = noFound, state_airport = True)

@staff.route('/report/viewRatings/<string:flight_num>/<string:dept_time>')
@staff_login_required
def checkRatings(flight_num, dept_time):
    #get airline name
    airline_name = session['airline_name']

    #fetch data
    cursor = conn.cursor()
    query = "SELECT airline_name,flight_num, dept_time, AVG(rate) as avg_rate \
        FROM rates \
        WHERE (airline_name,flight_num, dept_time) = (%s, %s, %s)"
    cursor.execute(query, (airline_name,flight_num, dept_time))
    data1 = cursor.fetchone()
    if data1["avg_rate"]:
        avg_rate = "{0:.2f}".format(float(data1["avg_rate"]))
    else: 
        noFound = "This Flight has no ratings yet"
        return render_template("report.html", noFound = noFound)

    query = "SELECT airline_name,flight_num, dept_time, cust_email, rate, comments \
            FROM rates \
            WHERE (airline_name,flight_num, dept_time) = (%s, %s, %s) "
    cursor.execute(query, (airline_name,flight_num, dept_time))
    data = cursor.fetchall()
    cursor.close()
    conn.commit()

    if data: 
        for each in data: 
            print (each)
        return render_template("report.html", avg_rate = avg_rate, ratings = data)
    else: 
        noFound = "This Flight has no ratings yet"
        return render_template("report.html", noFound = noFound)


@staff.route('/report/topAgent', methods = ['GET', 'POST'])
@staff_login_required
def viewTopAgent():
    #get airline name
    airline_name = session['airline_name']
    
    if request.method == 'POST': 
        #fetch data
        option = request.form.get("viewSelect")
        cursor = conn.cursor()
        #three options: 
        if option == "by_sales_month": 
            title = "Top 5 booking agents by ticket sales for the past month" 
            query = "SELECT  agent_email, COUNT(*) AS total_sales FROM ticket \
            WHERE agent_email IS NOT NULL AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 30 DAY AND NOW()\
            GROUP BY agent_email ORDER BY total_sales DESC LIMIT 5"
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            if data: 
                for each in data: 
                    print(each)
                return render_template("report.html", title = title, by_sales = data)
            else: 
                noFound = "There is an issue in displaying the information you want"
                return render_template("report.html", noFound = noFound)
        elif option == "by_sales_year":
            title = "Top 5 booking agents by ticket sales for the past year" 
            query = "SELECT  agent_email, COUNT(*) AS total_sales FROM ticket \
            WHERE agent_email IS NOT NULL AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR AND NOW()\
            GROUP BY agent_email ORDER BY total_sales DESC LIMIT 5"
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            if data: 
                for each in data: 
                    print(each)
                return render_template("report.html", title = title, by_sales = data)
            else: 
                noFound = "There is an issue in displaying the information you want"
                return render_template("report.html", noFound = noFound)
        else:
            title = "Top 5 booking agents by total commission for the past year" 
            query = "SELECT agent_email, SUM(sold_price) * 0.1 AS commission FROM ticket \
                     WHERE agent_email IS NOT NULL AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR AND NOW()\
                     GROUP BY agent_email ORDER BY commission DESC LIMIT 5"
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            if data: 
                for each in data: 
                    print(each)
                return render_template("report.html", title = title, by_commission = data)
            else: 
                noFound = "There is an issue in displaying the information you want"
                return render_template("report.html", noFound = noFound)         
              
    else: 
        title = "Default: Top 5 booking agents by ticket sales for the past month"
        cursor = conn.cursor()
        query = "SELECT  agent_email, COUNT(*) AS total_sales FROM ticket \
        WHERE agent_email IS NOT NULL AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 30 DAY AND NOW()\
        GROUP BY agent_email ORDER BY total_sales DESC LIMIT 5"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        if data: 
            for each in data: 
                print(each)
            return render_template("report.html", title = title, by_sales = data)
        else: 
            noFound = "There is an issue in displaying the information you want"
            return render_template("report.html", noFound = noFound)

@staff.route('/report/topCustomer')
@staff_login_required
def viewTopCustomer(): 
    #get airline name
    airline_name = session['airline_name']

    #start to fetch the data
    cursor = conn.cursor()
    query = "SELECT cust_email, COUNT(*) AS travel_times FROM ticket WHERE airline_name = %s \
    AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() \
    GROUP BY cust_email"

    cursor.execute(query,(airline_name))

    data1 = cursor.fetchall()
    max_times = 0
    for each in data1: 
        if each["travel_times"] > max_times:
            max_times = each["travel_times"]

    query2 = "SELECT cust_email, COUNT(*) AS travel_times FROM ticket WHERE airline_name = %s \
        GROUP BY cust_email HAVING travel_times = %s"
    cursor.execute(query2,(airline_name, max_times))
    data = cursor.fetchall()
    cursor.close()
    if data: 
        for each in data: 
            print(data)
        return render_template("report.html", passenger = data)
    else: 
        noFound = "There is an issue in displaying the information you want"
        return render_template("report.html", noFound = noFound)


@staff.route('/report/topCustomer/<string:email>')
@staff_login_required
def viewCustomerFlight(email): 
    #get airline name
    airline_name = session['airline_name']

    #fetch data
    cursor = conn.cursor()
    query = "SELECT airline_name, flight_num, dept_time, purchase_time, sold_price, cust_email FROM ticket WHERE cust_email = %s"
    cursor.execute(query,(email))
    data = cursor.fetchall()
    cursor.close()
    if data: 
        for each in data: 
            print(data)
        return render_template("report.html", people_flight = data)
    else: 
        noFound = "There is an issue in displaying the information you want"
        return render_template("report.html", noFound = noFound)

@staff.route('/report/salesReport/<string:message>', methods = ['GET', 'POST'])
@staff_login_required
def viewReport(message):
    #get airline name
    airline_name = session['airline_name']

    if message == "default":
        #access total_sales and date range
        cursor = conn.cursor()
        query = "SELECT DATE(NOW()) - INTERVAL 1 MONTH AS curr_prev, DATE(NOW()) AS current,  COUNT(*) AS total_sales \
            FROM ticket WHERE date(purchase_time) between DATE(NOW()) - INTERVAL 1 MONTH AND DATE(NOW()) and airline_name = %s"
        cursor.execute(query, (airline_name))
        info = cursor.fetchone()
        total_sales = info['total_sales'] #total sales
        from_date  = info['curr_prev'] # from_date
        to_date = info['current'] # to_date
        from_date_format = from_date
        to_date_format = to_date
        default = "Default:"
        title = "Total Sales for the Past Month"

    elif message == "date_range":
        #fetch input
        from_date = request.form["from_date"] 
        to_date = request.form["to_date"]
        if datetime.strptime(from_date, "%Y-%m-%d") > datetime.strptime(to_date, "%Y-%m-%d"):
            return render_template("flightManage.html", error = "The dates you entered are invalid.")
        from_date_format = datetime.strptime(from_date, '%Y-%m-%d')
        to_date_format = datetime.strptime(to_date, '%Y-%m-%d')   
        #access total_sales
        cursor = conn.cursor()
        query = "SELECT COUNT(*) as total_sales FROM ticket WHERE date(purchase_time) >= %s \
        AND date(purchase_time) <= %s and airline_name = %s"
        cursor.execute(query, (from_date, to_date, airline_name))
        info = cursor.fetchone()
        total_sales = info['total_sales'] #total sales
        default = ""
        title = ""

    else: 
        option = request.form.get("salesSelect")
        if option == "sales_past_month":
            #access total_sales and date range
            cursor = conn.cursor()
            query = "SELECT DATE(NOW()) - INTERVAL 1 MONTH AS curr_prev, DATE(NOW()) AS current,  COUNT(*) AS total_sales \
            FROM ticket WHERE date(purchase_time) between DATE(NOW()) - INTERVAL 1 MONTH AND DATE(NOW()) and airline_name = %s"
            cursor.execute(query, (airline_name))
            info = cursor.fetchone()
            total_sales = info['total_sales'] #total sales
            from_date  = info['curr_prev'] # from_date
            to_date = info['current'] # to_date
            from_date_format = from_date
            to_date_format = to_date
            default = ""
            title = "Total Sales for the Past Month"

        else: 
            #access total_sales and date range
            cursor = conn.cursor()
            query = "SELECT DATE(NOW()) AS current, DATE(NOW()) - INTERVAL 1 YEAR AS curr_prev , COUNT(*) as total_sales \
                FROM ticket WHERE date(purchase_time) between DATE(NOW()) - INTERVAL 1 YEAR AND DATE(NOW()) and airline_name = %s"
            cursor.execute(query, (airline_name))
            info = cursor.fetchone()
            print(info)
            total_sales = info['total_sales'] #total sales
            from_date  = info['curr_prev'] # from_date
            to_date = info['current'] # to_date
            from_date_format = from_date
            to_date_format = to_date
            default = ""
            title = "Total Sales for the Past Year"
    
    #access sales by month
    query = "SELECT YEAR(purchase_time) as year, MONTH(purchase_time) as month, COUNT(*) as total_sales \
    FROM ticket WHERE date(purchase_time) >= %s AND date(purchase_time) <= %s and airline_name = %s \
    GROUP BY year, month \
    ORDER BY year, month ASC"
    cursor.execute(query, (from_date, to_date, airline_name))
    raw_data = cursor.fetchall()
    print("raw", raw_data)
    cursor.close()


    #create empty dictionary
    sales_dict = {}
    start_year = from_date_format.year
    start_month = from_date_format.month
    end_year = to_date_format.year
    end_month = to_date_format.month
    sales_dict["{}-{}".format(start_year,start_month)] = 0
    print(start_year, start_month, end_year, end_month)

    if start_year != end_year:
        while start_year < end_year:
            while start_month < 12: 
                sales_dict["{}-{}".format(start_year,start_month + 1)] = 0
                start_month += 1
            start_year += 1
            start_month = 0
            if start_year == end_year: 
                while start_month < end_month: 
                    sales_dict["{}-{}".format(start_year,start_month + 1)] = 0
                    start_month += 1
    else: 
        while start_month < end_month: 
            sales_dict["{}-{}".format(start_year,start_month + 1)] = 0
            start_month += 1

    print("empty_dict:", sales_dict)

    for each in raw_data: 
        print(each)
        sales_dict["{}-{}".format(each["year"],each["month"])] = each["total_sales"]
    print("full_dict:", sales_dict)
    label_list = []
    values_list = []

    for keys in sales_dict: 
        label_list.append(keys)
        values_list.append(str(sales_dict[keys]))

    print("labels", label_list)
    print("values", values_list)

    try:
        mymax = max(values_list)
    except: 
        mymax = 100
    
    return render_template('report.html', sales = True, default = default, title = title, total_sales = total_sales, \
    max = mymax, from_date = from_date, to_date = to_date, labels=label_list, values=values_list)


@staff.route('/report/revenueCompare', methods = ['GET', 'POST'])
@staff_login_required
def revenueCompare():
    #get airline name
    airline_name = session['airline_name']

    cursor = conn.cursor()

    #colors: 
    colors = ["#FDB45C", "#FEDCBA"]
    if request.method == "POST":
        default = ""
        option = request.form.get("revSelect")
        if option == "rev_past_month":
            title = "Revenue comparison for the past month"
            query_direct = "SELECT SUM(sold_price) as total_price FROM ticket \
                WHERE agent_email IS NULL and DATE(purchase_time) BETWEEN DATE(NOW()) - INTERVAL 1 MONTH and DATE(NOW())"
            query_indirect = "SELECT SUM(sold_price) as total_price FROM ticket \
                WHERE agent_email IS NOT NULL and DATE(purchase_time) BETWEEN DATE(NOW()) - INTERVAL 1 MONTH and DATE(NOW())"
        else: 
            title = "Revenue comparison for the past year"
            query_direct = "SELECT SUM(sold_price) as total_price FROM ticket \
                WHERE agent_email IS NULL and DATE(purchase_time) BETWEEN DATE(NOW()) - INTERVAL 1 YEAR and DATE(NOW())"
            query_indirect = "SELECT SUM(sold_price) as total_price FROM ticket \
                WHERE agent_email IS NOT NULL and DATE(purchase_time) BETWEEN DATE(NOW()) - INTERVAL 1 YEAR and DATE(NOW())"

    else: 
        default = "Default:"
        title = "Revenue comparison for the past month"
        query_direct = "SELECT SUM(sold_price) as total_price FROM ticket \
            WHERE agent_email IS NULL and DATE(purchase_time) BETWEEN DATE(NOW()) - INTERVAL 1 MONTH and DATE(NOW())"
        query_indirect = "SELECT SUM(sold_price) as total_price FROM ticket \
            WHERE agent_email IS NOT NULL and DATE(purchase_time) BETWEEN DATE(NOW()) - INTERVAL 1 MONTH and DATE(NOW())"

    cursor.execute(query_direct)
    direct_sales = cursor.fetchone()

    cursor.execute(query_indirect)
    indirect_sales = cursor.fetchone()

    labels = ['direct_sales', 'indirect_sales']
    values = [float(direct_sales["total_price"]), float(indirect_sales["total_price"])]

    print(values)

    try:
        mymax = max(values)
    except: 
        mymax = 100000

    return render_template("report.html", default = default, title = title, revenue = True, \
        max = mymax, set = zip(values, labels, colors))


@staff.route('/report/topDestination', methods = ['GET','POST'])
@staff_login_required
def topDestination(): 
    #get airline name
    airline_name = session['airline_name']
    
    #different query
    if request.method == "POST":
        chosen = request.form.get("seeSelect")
        if chosen == "by_3month": 
            title = "Top Three Destinations for the Past Three Months"
            query = "SELECT arr_at, city, count(*) as visit_time \
                    FROM ticket NATURAL JOIN flight as S, airport \
                    WHERE S.arr_at  = airport.name AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 3 MONTH and NOW()\
                    GROUP BY arr_at ORDER BY visit_time DESC LIMIT 3"
        else: 
            title = "Top Three Destinations for the Past Year"
            query = "SELECT arr_at, city, count(*) as visit_time \
                    FROM ticket NATURAL JOIN flight as S, airport \
                    WHERE S.arr_at  = airport.name AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR and NOW()\
                    GROUP BY arr_at ORDER BY visit_time DESC LIMIT 3"
    else: 
        title = "Default: Top Three Destinations for the Past Three Months"
        query = "SELECT arr_at, city, count(*) as visit_time \
                FROM ticket NATURAL JOIN flight as S, airport \
                WHERE S.arr_at  = airport.name AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 3 MONTH and NOW() \
                GROUP BY arr_at ORDER BY visit_time DESC LIMIT 3"
    #execute the query 
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    if data:
        for each in data: 
            print(data)
        return render_template("report.html", title = title, destinations = data)
    else: 
        noFound = "Sorry, there's an issue in displaying the information"
        return render_template("report.html", noFound = noFound, destinations = data)













