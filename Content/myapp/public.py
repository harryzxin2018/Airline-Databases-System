# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect
from database import conn
from decimal import *
from datetime import datetime

public = Blueprint('public', __name__)

#Define a route to hello function
@public.route('/')
def hello():
    return render_template('index.html')

@public.route('/searchFlights', methods=['GET', 'POST'])
def searchFlights():
    #grabs information from the forms
    dept_from = request.form['dept_from']
    arr_at = request.form['arr_at']
    dept_date = request.form['dept_date']
    return_date = request.form['return_date']

    if datetime.strptime(dept_date, "%Y-%m-%d") < datetime.now():
        return render_template("index.html", error = "The dates you entered have already passed.")

    #open cursor
    cursor = conn.cursor()

    #excutes query for flight
    query = "select * from flight natural join airplane, airport as A, airport as B \
            where flight.dept_from = A.name and flight.arr_at = B.name \
            and (A.name = %s or A.city = %s) and (B.name = %s or B.city = %s) \
            and date(dept_time) = %s "
    cursor.execute(query, (dept_from, dept_from, arr_at, arr_at, dept_date))
    #store the results
    data = cursor.fetchall()

    if return_date:
        if datetime.strptime(dept_date, "%Y-%m-%d") > datetime.strptime(return_date, "%Y-%m-%d"):
            return render_template("search.html", error = "The dates you entered are invalid.")
        query2 = "select * from flight natural join airplane, airport as A, airport as B \
                where flight.dept_from = A.name and flight.arr_at = B.name \
                and (A.name = %s or A.city = %s) and (B.name = %s or B.city = %s) \
                and date(dept_time) = %s "
        cursor.execute(query2, ( arr_at, arr_at, dept_from, dept_from, return_date))

    #store the results
    data2 = cursor.fetchall()
    print(data2)
    

    for each in data:
        #executes query for ticket sold 
        queryTicketNum = "select count(*) from ticket natural join flight natural join airplane where airline_name = %s and flight_num = %s and dept_time=%s"
        cursor.execute(queryTicketNum, ( each['airline_name'], each['flight_num'], each['dept_time']))
        ticketNum = cursor.fetchone()
        rate = (each['seats'] - ticketNum['count(*)']) / each['seats']
        if rate > 0.7:
            each['current_price'] = Decimal(1.2) *each['base_price']
    
    for each in data2:
        #executes query for ticket sold 
        queryTicketNum = "select count(*) from ticket natural join flight natural join airplane where airline_name = %s and flight_num = %s and dept_time=%s"
        cursor.execute(queryTicketNum, ( each['airline_name'], each['flight_num'], each['dept_time']))
        ticketNum = cursor.fetchone()
        rate = (each['seats'] - ticketNum['count(*)']) / each['seats']
        if rate > 0.7:
            each['current_price'] = Decimal(1.2) *each['base_price']
    conn.commit()
    cursor.close()

    error = None
    if data: #input is valid
        if return_date: # round trip·
            if data2: 
                return render_template("search.html", flights = data, returnFlights = data2)
            else: 
                error = "The Return Flight You are Searching Is Empty"
                return render_template("search.html", error = error)
        else: #one way trip
            return render_template("search.html", flights = data)
    else: 
        #returns an error message to the html page
        error = "The Flight You are Searching Is Empty"
        return render_template("search.html", error = error)

@public.route('/checkFlight', methods=['GET', 'POST'])
def checkFlight():
    #grabs information from the forms
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_date = request.form['dept_date']
    arr_date = request.form['arr_date']

    #open cursor
    cursor = conn.cursor()

    #excutes query
    if dept_date and arr_date: 
        query = "select * from flight \
            where airline_name = %s and flight_num = %s and date(dept_time) = %s and date(arr_time) = %s"
        cursor.execute(query, (airline_name, flight_num, dept_date, arr_date))
    elif dept_date:
        query = "select * from flight \
            where airline_name = %s and flight_num = %s and date(dept_time) = %s"
        cursor.execute(query, (airline_name, flight_num, dept_date))
    elif arr_date:
        query = "select * from flight \
            where airline_name = %s and flight_num = %s and date(arr_time) = %s"
        cursor.execute(query, (airline_name, flight_num, arr_date))
    else: 
        pass

    #store the results
    data3 = cursor.fetchall()

    cursor.close()
    conn.commit()
    error = None

    if data3: 
        return render_template("check.html", status = data3)
    else: 
        error = "The Flight You are Searching Is Empty"
        return render_template("check.html", error = error)

