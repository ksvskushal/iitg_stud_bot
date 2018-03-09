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

    intent_name = req.get("result").get("metadata").get("intentName");
    if intent_name == "specific-course-location":
        res = get_location(req,res)
    elif intent_name == "exam-timings":
        res = get_exam_timings(req,res)
    elif intent_name == "timings-nfl-class":
        res = get_class_timings_nfl(req,res)

    print("Response:")
    res = json.dumps(res, indent=4)
    print (res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def get_week_day():
    week_day_dict = {'0':'MON', '1':'TUE', '2':'WED', '3':'THU', '4':'FRI', '5':'SAT', '6':'SUN'}
    return week_day_dict[str(datetime.datetime.today().weekday())]

def get_class_timings_nfl(req,res):
    week_day = get_week_day()

    week_day = "TUE"

    nfl = req.get("result").get("parameters").get("time")

    student_list = {    
        '1338471136207322': '160101076',
        '1653617614727730': '150101031'
    }

    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    roll_no = student_list[sender_id]
    hour = datetime.datetime.now().hour % 12

    hour = str(hour)
    hour = "{0:0>2}".format(hour)
    hour = hour + ":00:00"

    conn = mysql.connect()
    cursor = conn.cursor()

    if nfl == "first" or nfl == "First": 
        query = "SELECT course_id, start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND day = \"" + week_day+ "\" ORDER BY start_time LIMIT 1"
    elif nfl == "last" or nfl ==  "Last":
        query = "SELECT course_id, start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND day = \"" + week_day+ "\" ORDER BY start_time DESC LIMIT 1"
    elif nfl == "next" or nfl ==  "Next":
        query = "SELECT course_id, start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND day = \"" + week_day+ "\" AND start_time > \""+hour+"\"ORDER BY start_time LIMIT 1"

    cursor.execute(query)

    data = cursor.fetchall()
    # data = data[0][0]
    print(data)
    data = data[0]
    # out_list = json.dumps(data)
    out_string = "You have " + data[0] + " from " + data[1] + " in " + data[2]

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

def get_location(req,res):

    week_day = get_week_day

    course_id = req.get("result").get("parameters").get("course-name")
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT room_number FROM ScheduledIn WHERE course_id = \"" + course_id + "\" AND day = \"" + week_day + "\";"

    cursor.execute(query)

    data = cursor.fetchall()
    data = data[0]

    out_string = json.dumps(data)
    out_string = "The Class is in " + out_string

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

def get_exam_timings(req,res):

    course_id = req.get("result").get("parameters").get("course-id")
    sem = req.get("result").get("parameters").get("exam")
    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.datetime.now()
    betw_mid_end = datetime.datetime(2018, 4, 5)

    print("sem is " + sem)
    if sem == "midsem":
        query = "SELECT exam_date,start_time,end_time FROM mid_ett WHERE course_id = \"" + course_id + "\";"
    elif sem == "endsem":
        query = "SELECT exam_date,start_time,end_time FROM end_ett WHERE course_id = \"" + course_id + "\";"
    elif sem ==  "":
        if now < betw_mid_end:
            query = "SELECT exam_date,start_time,end_time FROM mid_ett WHERE course_id = \"" + course_id + "\";"
        else:
            query = "SELECT exam_date,start_time,end_time FROM end_ett WHERE course_id = \"" + course_id + "\";"

    cursor.execute(query)

    data = cursor.fetchall()
    # data = data[0][0]
    print(data)
    data = data[0]
    # out_list = json.dumps(data)
    out_string = "The Exam is on " + data[0] + " from " + data[1] + " to " + data[2]

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print "Starting app on port %d" % port
    app.run(debug=True, port=port, host='0.0.0.0')
