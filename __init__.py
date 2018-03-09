#!/usr/bin/env python

import datetime
import urllib
import httplib
import json
import os

from flask import Flask,request,make_response
from flaskext.mysql import MySQL
from collections import defaultdict

mysql= MySQL()

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'buddy'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route("/hello")
def hello():
    return "Hello, I love Digital Ocean!"

@app.route("/webhook", methods=['POST'])
def test():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    input = json.dumps(req, indent=4)
    print (input)

    res = {
        "speech": "Failed!",
        "displayText": "Failed!",
        "source": "IITG-Student-Buddy"
    }

    if req.get("result").get("metadata").get("intentName")=="specific-course-location":
        res = get_location(req,res)

    print("Response:")
    res = json.dumps(res, indent=4)
    print (res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print "Starting app on port %d" % port
    app.run(debug=True, port=port, host='0.0.0.0')

def get_location(req,res):

    week_day_dict = {'0':'MON', '1':'TUE', '2':'WED', '3':'THU', '4':'FRI', '5':'SAT', '6':'SUN'}
    week_day = week_days[datetime.datetime.today().weekday()]

    course_id = req.get("result").get("parameters").get("course-name")
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT room_number FROM ScheduledIn WHERE course_id = \"" + course_id + "\" AND day = \"" + week_day + "\";"

    cursor.execute(query)

    data = cursor.fetchall()

    stri = json.dumps(data)

    return {
        "speech": stri,
        "displayText": stri,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }