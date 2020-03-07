# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify
from database import conn
import datetime
from login_required import *
from decimal import *
import copy


customer = Blueprint('customer', __name__)

@customer.route('/customerHome')
@customer_login_required
def customerHome():
    email = session['email']
    username = session['username']
    return render_template('customerHome.html', username = username)

@customer.route('/logout')
@customer_login_required
def logout():
    session.clear()
    return redirect(url_for('register_login.login'))

@customer.route('/viewMyFlights')
@customer_or_agent_login_required
def viewMyFlights():
    if session['role'] == 'customer':
        email = session['email']
        username = session['username']
        cursor = conn.cursor()
        current_date = datetime.datetime.now()
        query = "select * from ticket natural join flight natural join airport as A, airport as B where cust_email = %s and dept_time > %s and dept_from = A.name and arr_at = B.name"
        cursor.execute(query, (email, current_date))
        data1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('viewMyFlights.html', flights=data1, role = 'customer')
    elif session['role'] == 'agent':
        email = session['email']
        cursor = conn.cursor()
        current_date = datetime.datetime.now()
        query = "select * from ticket natural join flight natural join airport as A, airport as B where agent_email = %s and dept_time > %s and dept_from = A.name and arr_at = B.name"
        cursor.execute(query, (email, current_date))
        data1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('viewMyFlights.html',  flights=data1, role = 'agent')

@customer.route('/searchForFlights')
@customer_or_agent_login_required
def customerSearchForFlights():
    return render_template('searchForFlights.html', role = session['role'])

@customer.route('/searchFlightsResults', methods=['GET', 'POST'])
@customer_or_agent_login_required
def searchFlights():
    #grabs information from the forms
    dept_from = request.form['dept_from']
    arr_at = request.form['arr_at']
    dept_date = request.form['dept_date']
    return_date = request.form['return_date']

    if datetime.datetime.strptime(dept_date, "%Y-%m-%d") < datetime.datetime.now():
        return render_template("searchForFlights.html", error = "The dates you entered have already passed.")

    #open cursor
    cursor = conn.cursor()

    #excutes query for flight
    query = "select * from flight natural join airplane, airport as A, airport as B \
        where flight.dept_from = A.name and flight.arr_at = B.name and (A.name = %s or A.city = %s) and (B.name = %s or B.city = %s) and date(dept_time) = %s"
    cursor.execute(query, (dept_from, dept_from, arr_at, arr_at, dept_date))
    #store the results
    data = cursor.fetchall()

    if return_date:
        if datetime.datetime.strptime(dept_date, "%Y-%m-%d") > datetime.datetime.strptime(return_date, "%Y-%m-%d"):
            return render_template("searchForFlights.html", error = "The dates you entered are invalid.")
        query2 = "select * from flight natural join airplane, airport as A, airport as B where flight.dept_from = A.name and flight.arr_at = B.name and (A.name = %s or A.city = %s) and (B.name = %s or B.city = %s) and date(dept_time) = %s "
        cursor.execute(query2, ( arr_at, arr_at, dept_from, dept_from, return_date))

    #store the results
    data2 = cursor.fetchall()

    data_copy = copy.deepcopy(data)
    for i, each in enumerate(data):
        #excutes query for ticket sold 
        queryTicketNum = "select count(*) from ticket natural join flight natural join airplane where airline_name = %s and flight_num = %s and dept_time=%s"
        cursor.execute(queryTicketNum, ( each['airline_name'], each['flight_num'], each['dept_time']))
        ticketNum = cursor.fetchone()
        rate = ticketNum['count(*)'] / each['seats']
        each['index'] = i
        if ticketNum['count(*)'] == each['seats']:
            each['seatStatus'] = 'full'
        else:
            each['seatStatus'] = 'normal'
        if rate > 0.7:
            each['current_price'] = float(round(Decimal(1.2) *each['base_price'], 2))
        else:
            each['current_price'] = float(each['base_price'])
        each['base_price'] = float(each['base_price'])
    
    data2_copy = copy.deepcopy(data2)      
    for i, each in enumerate(data2):
        #excutes query for ticket sold 
        queryTicketNum = "select count(*) from ticket natural join flight natural join airplane where airline_name = %s and flight_num = %s and dept_time=%s"
        cursor.execute(queryTicketNum, ( each['airline_name'], each['flight_num'], each['dept_time']))
        ticketNum = cursor.fetchone()
        each['index'] = i
        rate = ticketNum['count(*)'] / each['seats']
        if ticketNum['count(*)'] == each['seats']:
            each['seatStatus'] = 'full'
        else:
            each['seatStatus'] = 'normal'
        if rate > 0.7:
            each['current_price'] = float(round(Decimal(1.2) *each['base_price'], 2))
        else:
            each['current_price'] = float(each['base_price'])
        each['base_price'] = float(each['base_price'])
    conn.commit()
    cursor.close()

    error = None
    if data: #input is valid
        # for each in data: #for debugging
        #     print(each)
        if return_date: # round trip·
            if data2: 
                return render_template("searchForFlights.html", flights = data, returnFlights = data2,  role = session['role'])
            else: 
                error = "The Return Flight You are Searching Is Empty"
                return render_template("searchForFlights.html", error = error,  role = session['role'])
        else: #one way trip
            return render_template("searchForFlights.html", flights = data,  role = session['role'])
    else: 
        #returns an error message to the html page
        error = "The Flight You are Searching Is Empty"
        return render_template("searchForFlights.html", error = error,  role = session['role'])

@customer.route('/purchaseTickets', methods=['GET', 'POST'])
@customer_or_agent_login_required
def purchaseTickets():
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_time = request.form['dept_time']
    current_price = request.form['price']
    airline_name2 = request.form['airline_name2']
    flight_num2 = request.form['flight_num2']
    dept_time2 = request.form['dept_time2']
    current_price2 = request.form['price2']
    total = float(current_price)+float(current_price2)
    #open cursor
    cursor = conn.cursor()
    #excutes query for flight
    query = "select * from flight natural join airplane, airport as A, airport as B where airline_name = %s and flight_num = %s and dept_time = %s and dept_from = A.name and arr_at = B.name"
    cursor.execute(query, (airline_name, flight_num, dept_time))
    #store the results
    data = cursor.fetchone()
    data['current_price'] = current_price
    data2 = 0
    if airline_name2 != '':
        query = "select * from flight natural join airplane, airport as A, airport as B where airline_name = %s and flight_num = %s and dept_time = %s and dept_from = A.name and arr_at = B.name"
        cursor.execute(query, (airline_name2, flight_num2, dept_time2))
        data2 = cursor.fetchone()
        data2['current_price'] = current_price2
    conn.commit()
    cursor.close()
    print(airline_name)
    return render_template("purchaseTickets.html", flight = data, return_flight = data2, total = total, role=session['role'])

@customer.route('/purchaseDetails', methods=['GET', 'POST'])
@customer_or_agent_login_required
def purchaseDetails():
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_time = request.form['dept_time']
    current_price = request.form['price']
    airline_name2 = request.form['airline_name2']
    flight_num2 = request.form['flight_num2']
    dept_time2 = request.form['dept_time2']
    current_price2 = request.form['price2']
    card_type = request.form['card_type']
    card_num = request.form['card_num']
    name_on_card = request.form['name_on_card']
    expr_date = request.form['expr_date']
    cursor = conn.cursor()
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    cust_email = session['email']
    if session['role'] == 'agent':
        cust_email = request.form['cust_email']
    query = "select count(*) from rates where cust_email = %s and  ((airline_name,flight_num, dept_time) = (%s, %s, %s) or (airline_name,flight_num, dept_time) = (%s, %s, %s)) "
    cursor.execute(query, (cust_email, airline_name, flight_num, dept_time, airline_name2, flight_num2, dept_time2))
    num = cursor.fetchone()
    if num['count(*)'] > 0:
        return "Purchased"
    
    if session['role'] == 'agent':
        query = "select count(*) from customer where email = %s"
        cursor.execute(query, cust_email)
        num = cursor.fetchone()
        if num['count(*)'] == 0:
            return "Failure"
        #executes query for flight
        query = "insert into ticket values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (str(datetime.datetime.now().timestamp()), current_price, card_type, card_num, name_on_card, expr_date, time, session['email'], cust_email, airline_name, flight_num, dept_time))
        #store the results
        if len(airline_name2) > 0:
            query = "insert into ticket values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (str(datetime.datetime.now().timestamp()), current_price2, card_type, card_num, name_on_card, expr_date, time, session['email'], cust_email, airline_name2, flight_num2, dept_time2))
    else:
        #executes query for flight
        query = "insert into ticket values (%s, %s, %s, %s, %s, %s, %s, null, %s, %s, %s, %s)"
        cursor.execute(query, (str(datetime.datetime.now().timestamp()), current_price, card_type, card_num, name_on_card, expr_date, time, session['email'], airline_name, flight_num, dept_time))
        #store the results
        if len(airline_name2) > 0:
            query = "insert into ticket values (%s, %s, %s, %s, %s, %s, %s, null, %s, %s, %s, %s)"
            cursor.execute(query, (str(datetime.datetime.now().timestamp()), current_price2, card_type, card_num, name_on_card, expr_date, time, session['email'], airline_name2, flight_num2, dept_time2))
    conn.commit()
    cursor.close()
    return "Success"

@customer.route('/comments')
@customer_login_required
def comments():
    #open cursor
    cursor = conn.cursor()
    #excutes query for flight
    query = "select * from ticket natural join flight natural join airport as A, airport as B where cust_email = %s and dept_time < %s and dept_from = A.name and arr_at = B.name"
    cursor.execute(query, (session['email'], datetime.datetime.now()))
    #store the results
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return render_template("comments.html", flights = data)

@customer.route('/giveComments/<string:ticket_id>', methods=['GET', 'POST'])
@customer_login_required
def giveComments(ticket_id):
    if request.method == 'POST':
        rate = request.form['rate']
        comment = request.form['comment']
        cursor = conn.cursor()
        query = "select * from ticket where ticket_id = %s"
        cursor.execute(query, (ticket_id))
        ticket = cursor.fetchone()
        query = "select * from rates where cust_email = %s and airline_name = %s and flight_num = %s and dept_time = %s"
        cursor.execute(query, (session['email'], ticket['airline_name'], ticket['flight_num'],ticket['dept_time']))
        data = cursor.fetchone()
        if data == None:
            query = "insert into rates values (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (session['email'], ticket['airline_name'], ticket['flight_num'],ticket['dept_time'], rate, comment))
        else:
            query = "update rates set rate = %s, comments = %s where cust_email = %s and airline_name = %s and flight_num = %s and dept_time = %s"
            cursor.execute(query, (rate, comment, session['email'], ticket['airline_name'], ticket['flight_num'], ticket['dept_time']))
        conn.commit()
        cursor.close()
        return redirect('/comments')
    else:
        cursor = conn.cursor()
        #excutes query for flight
        query = "select * from ticket natural join flight natural join airport as A, airport as B where ticket_id = %s and dept_from = A.name and arr_at = B.name"
        cursor.execute(query, (ticket_id))
        #store the results
        data = cursor.fetchone()

        query = "select * from rates where cust_email = %s and airline_name = %s and flight_num = %s and dept_time = %s"
        cursor.execute(query, (session['email'], data['airline_name'], data['flight_num'], data['dept_time']))
        #store the results
        rates = cursor.fetchone()
        conn.commit()
        cursor.close()
        return render_template('giveComments.html', flight = data, rates = rates)

@customer.route('/trackMySpending', methods=['GET', 'POST'])
@customer_login_required
def trackMySpending():
    if request.method == 'POST':
        to_date = request.form['to_date']
        from_date = request.form['from_date']
        if datetime.datetime.strptime(from_date, "%Y-%m-%d") > datetime.datetime.strptime(to_date, "%Y-%m-%d"):
            return render_template('trackMySpending.html', error="The dates you entered are invalid.")
        to_date_format = datetime.datetime.strptime(to_date, '%Y-%m-%d')
        from_date_format = datetime.datetime.strptime(from_date, '%Y-%m-%d')
        year = to_date_format.year
        month = to_date_format.month
        date = to_date_format.day
        from_year = from_date_format.year
        from_month = from_date_format.month
        from_date_date = from_date_format.day
        from_date_string = '{}-{}-{}'.format(from_year, from_month, from_date_date)
        to_date_string = '{}-{}-{}'.format(year, month, date)
        monthnum = (year - from_year)*12 + month - from_month
    else:
        to_date = datetime.datetime.now()
        year = to_date.year
        from_year = to_date.year - 1
        month = to_date.month
        date = to_date.day
        monthnum = 5
        string = '{} 1 {} 00:00'.format(month, from_year)
        from_date = datetime.datetime.strptime(string, '%m %d %Y %H:%M')
        from_date_string = '{}-{}-{}'.format(from_year, month, date)
        to_date_string = '{}-{}-{}'.format(year, month, date)

    cursor = conn.cursor()
    query = "SELECT COALESCE( SUM(sold_price), 0) as total_spending FROM ticket WHERE purchase_time > %s AND purchase_time < %s AND cust_email = %s"
    cursor.execute(query, (from_date, to_date, session['email']))
    total_spending = float(cursor.fetchone()['total_spending'])
    print(month)
    if month < 12:
        string = '{} 1 {} 00:00'.format(month+1, year + 1)
    else:
        string = '{} 1 {} 00:00'.format(1, year + 2)
    temp_date = datetime.datetime.strptime(string, '%m %d %Y %H:%M')
    
    labels = []
    values = []
    temp_year = year
    temp_month = month
    for i in range(0,monthnum + 1):
        this_date = temp_date
        this_month = temp_month
        temp_month = (month-i)%12
        if temp_month == 0:
            temp_month = 12
        if temp_month > this_month:
            temp_year = temp_year - 1
        string = '{} 1 {} 00:00'.format(temp_month, temp_year)
        temp_date = datetime.datetime.strptime(string, '%m %d %Y %H:%M')
        query = "SELECT COALESCE( SUM(sold_price), 0)  as monthly_spending FROM ticket WHERE purchase_time > %s and purchase_time < %s AND cust_email = %s"
        cursor.execute(query, (temp_date, this_date, session['email']))
        data = cursor.fetchone()
        label = '{}-{}'.format(temp_year, temp_month)
        labels.append(label)
        values.append(float(data['monthly_spending']))
    cursor.close()
    labels.reverse()
    values.reverse()
    print(labels)
    try:
        mymax = max(values)
    except:
        mymax = 100
    return render_template('trackMySpending.html', total_spending = total_spending, max = mymax, from_date = from_date_string, to_date = to_date_string,labels=labels, values=values)