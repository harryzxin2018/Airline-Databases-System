# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, url_for, redirect
from database import conn
from public import public
from register_login import register_login
from customer import customer
from agent import agent
from staff import staff

#Initialize the app from Flask
app = Flask(__name__)

#public info page
app.register_blueprint(public)

#login & register page
app.register_blueprint(register_login)

#customer homepage
app.register_blueprint(customer)

#staff homepage
app.register_blueprint(staff)

#booking agent homepage
app.register_blueprint(agent)

app.secret_key = 'some key that you will never guess'

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('localhost', 5000, debug = True)