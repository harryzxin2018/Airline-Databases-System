# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify
from database import conn
from login_required import agent_login_required
import datetime
from decimal import *

agent = Blueprint('agent', __name__)

@agent.route("/agentHome")
@agent_login_required
def agentHome():
    email = session['email']
    return render_template('agentHome.html')

@agent.route("/commission", methods=['GET', 'POST'])
@agent_login_required
def commission():
    if request.method == "POST":
        to_date = request.form['to_date']
        from_date = request.form['from_date']
        if datetime.datetime.strptime(from_date, "%Y-%m-%d") > datetime.datetime.strptime(to_date, "%Y-%m-%d"):
            return render_template("commission.html", error = "The dates you entered are invalid.")
        cursor = conn.cursor()
        query = "SELECT IFNULL(SUM(sold_price) , 0) as total_price, IFNULL(COUNT(*) , 0) as ticket_num FROM ticket WHERE DATE(purchase_time) BETWEEN %s AND %s AND agent_email = %s"
        cursor.execute(query, (from_date, to_date, session['email']))
        data = cursor.fetchone()
        conn.commit()
        cursor.close()
        total_price = "{0:.2f}".format(float(data['total_price'])*0.1)
        average_commission = "{0:.2f}".format( float(data['total_price'])*0.1/float(data['ticket_num']))
        return render_template("commission.html", total_price = total_price, average_commission = average_commission, ticket_num = data['ticket_num'], from_date = from_date, to_date = to_date)
    else:
        cursor = conn.cursor()
        query = "SELECT IFNULL(SUM(sold_price) , 0) as total_price, IFNULL(COUNT(*) ,0) as ticket_num FROM ticket WHERE DATE(purchase_time) BETWEEN NOW() - INTERVAL 30 DAY AND NOW() + INTERVAL 1 DAY AND agent_email = %s"
        cursor.execute(query, (session['email']))
        data = cursor.fetchone()
        conn.commit()
        cursor.close()
        print("data:", data)
        if data['total_price'] != 0 and data['ticket_num'] != 0: 
            total_price = "{0:.2f}".format(float(data['total_price'])*0.1)
            average_commission = "{0:.2f}".format( float(data['total_price'])*0.1/float(data['ticket_num']))
            ticket_num = data['ticket_num']
        else: 
            total_price = 0
            average_commission = 0
            ticket_num = 0
        return render_template("commission.html", total_price = total_price, average_commission = average_commission, ticket_num = ticket_num)
        
@agent.route("/topCustomers")
@agent_login_required
def topCustomers():
    cursor = conn.cursor()
    query = "SELECT cust_email, count(*) as num FROM ticket WHERE DATE(purchase_time) BETWEEN NOW() - INTERVAL 6 MONTH AND NOW() + INTERVAL 1 DAY AND agent_email = %s GROUP BY cust_email ORDER BY num DESC LIMIT 5"
    cursor.execute(query, (session['email']))
    data = cursor.fetchall()
    print(data)
    labels = []
    values = []
    for each in data:
        labels.append(each['cust_email'])
        values.append(each['num'])
    try:
        mymax = max(values)
    except:
        mymax = 10

    query = "SELECT cust_email, SUM(sold_price) as sum FROM ticket WHERE DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() + INTERVAL 1 DAY AND agent_email = %s GROUP BY cust_email ORDER BY sum DESC LIMIT 5"
    cursor.execute(query, (session['email']))
    data2 = cursor.fetchall()
    print(data2)
    labels2 = []
    values2 = []
    for each in data2:
        labels2.append(each['cust_email'])
        values2.append(float(each['sum'])/10)
    try:
        mymax2 = max(values2)
    except:
        mymax2 = 10

    conn.commit()
    cursor.close()
    return render_template("topCustomers.html", max = mymax, max2 = mymax2, labels=labels, values=values, labels2=labels2, values2=values2 )