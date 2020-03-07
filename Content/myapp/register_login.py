# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, session, url_for, redirect
from decimal import *
from database import conn
from passlib.hash import sha256_crypt

register_login = Blueprint('register_login', __name__)

#Define route for login
@register_login.route('/login')
def login():
  return render_template('login.html')

#Define route for register
@register_login.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@register_login.route('/loginAuthCustomer', methods=['GET', 'POST'])
def loginAuthCustomer():
    #grabs information from the forms 
    email = request.form['email']
    password = request.form['password']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    conn.commit()
    error = None
    if(data):
        if(sha256_crypt.verify(password, data['password'])):
            #creates a session for the the user
            #session is a built in
            session['email'] = email
            session['role'] = 'customer'
            session['username'] = data['name']
            return redirect(url_for('customer.customerHome'))
        else:
            #returns an error message to the html page
            error = 'Invalid password'
            return render_template('login.html', error=error)
    else:
        #returns an error message to the html page
        error = 'Invalid username'
        return render_template('login.html', error=error)

@register_login.route('/loginAuthAgent', methods=['GET', 'POST'])
def loginAuthAgent():
    email = request.form['email']
    password = request.form['password']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM booking_agent WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    conn.commit()
    error = None
    if(data):
        if(sha256_crypt.verify(password, data['password'])):
            #creates a session for the the user
            #session is a built in
            session['email'] = email
            session['role'] = 'agent'
            return redirect(url_for('agent.agentHome'))
        else:
            #returns an error message to the html page
            error = 'Invalid password'
            return render_template('login.html', error=error)
    else:
        #returns an error message to the html page
        error = 'Invalid username'
        return render_template('login.html', error=error)

@register_login.route('/loginAuthStaff', methods=['GET', 'POST'])
def loginAuthStaff():
    username = request.form['username']
    password = request.form['password']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    cursor.close()
    conn.commit()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        if(sha256_crypt.verify(password, data['password'])):
            #creates a session for the the user
            #session is a built in
            session['username'] = username
            session['role'] = "staff"
            session['first_name'] = data["first_name"]
            session['last_name'] = data["last_name"]
            session['airline_name'] = data["airline_name"]
            return redirect(url_for('staff.staffHome'))
        else:
            #returns an error message to the html page
            error = 'Invalid password'
            return render_template('login.html', error=error)
    else:
        #returns an error message to the html page
        error = 'Invalid username'
        return render_template('login.html', error=error)
    

#Authenticates the register
@register_login.route('/registerAuthCustomer', methods=['GET', 'POST'])
def registerAuthCustomer():
    #grabs information from the forms
    email = request.form['email']
    password = sha256_crypt.encrypt(request.form['password'])
    name = request.form['name']
    building_num = request.form['building_num']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_num = request.form['phone_num']
    passport_num = request.form['passport_num']
    passport_expr = request.form['passport_expr']
    passport_country = request.form['passport_country']
    DOB = request.form['DOB']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        conn.commit()
        cursor.close()
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, password, name, building_num, street, city, state, phone_num, passport_num, passport_expr, passport_country, DOB, 0))
        conn.commit()
        cursor.close()
        return render_template('index.html')

@register_login.route('/registerAuthAgent', methods=['GET', 'POST'])
def registerAuthAgent():    
    email = request.form['email']
    password = sha256_crypt.encrypt(request.form['password'])
    agent_id = request.form['id']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM booking_agent WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    query = 'SELECT * FROM booking_agent WHERE agent_id = %s'
    cursor.execute(query, (agent_id))
    data2 = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        cursor.close()
        conn.commit()
        return render_template('register.html', error = error)
    elif (data2):
        #If the previous query returns data, then user exists
        error = "This agent id already exists"
        cursor.close()
        conn.commit()
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO booking_agent VALUES(%s, %s, %s, %s)'
        cursor.execute(ins, (email, password, agent_id, 0))
        conn.commit()
        cursor.close()
        return render_template('index.html')

@register_login.route('/registerAuthStaff', methods=['GET', 'POST'])
def registerAuthStaff(): 
    username = request.form['username']
    password = sha256_crypt.encrypt(request.form['password'])
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    DOB = request.form['DOB']
    airline_name = request.form['airline_name']
    phone_number = request.form['phone_number']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        cursor.close()
        conn.commit()
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, first_name, last_name, DOB, airline_name))
        if ";" in phone_number: 
            phone_number_lst = phone_number.split(";")
            for item in phone_number_lst: 
                ins = 'INSERT INTO staff_phone VALUES(%s, %s)'
                cursor.execute(ins, (username, item.strip()))
        else: 
            ins = 'INSERT INTO staff_phone VALUES(%s, %s)'
            cursor.execute(ins, (username, phone_number))
        conn.commit()
        cursor.close()
        return render_template('index.html')
