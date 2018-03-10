#!/usr/bin/env python

import datetime
import calendar
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
    elif intent_name == "schedule-specific-day":
        res = get_schedule_specific_day(req,res)
    elif intent_name == "specific-course-time":
        res = get_specific_course_time(req,res)

    print("Response:")
    res = json.dumps(res, indent=4)
    print (res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def get_week_day(diff):
    week_day_dict = {'0':'MON', '1':'TUE', '2':'WED', '3':'THU', '4':'FRI', '5':'SAT', '6':'SUN'}
    return week_day_dict[str((datetime.datetime.today().weekday() + diff) % 7)]

def get_schedule_specific_day(req,res):

    out_string = ""

    week_day = req.get("result").get("parameters").get("week_day")

    if week_day == "TOD":
        week_day = get_week_day(0)

    if week_day == "TOM":
        week_day = get_week_day(1)

    if not week_day:
        week_day = req.get("result").get("parameters").get("date")
        if week_day:
            year, month, day = (int(x) for x in week_day.split('-'))    
            ans = datetime.date(year, month, day)
            ans= ans.strftime("%A")
            ans = ans.upper()
            week_day = ans[0:3]

    print (week_day)
    
    if not week_day:
        week_day = get_week_day(0)
        if week_day == "SAT" or week_day == "SUN":
            out_string += "No classes today! \n This is the time-table for next Monday.\n"
            week_day = "MON"

    student_list = {    
        '1338471136207322': '160101076',
        '1653617614727730': '150101031',
        '1852825864791150': '150123004',
    }

    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    roll_no = student_list[sender_id]

    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT course_id, start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND day = \"" + week_day+ "\" ORDER BY start_time;"

    cursor.execute(query)

    data = cursor.fetchall()
    # data = data[0][0]
    print(data)
    print(len(data))

    for k in data:
        out_string += "You have " + k[0] + " from " + k[1] + " in " + k[2] + "\n"

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

def get_specific_course_time(req,res):

    out_string = ""

    week_day = req.get("result").get("parameters").get("week_day")
    course_id = req.get("result").get("parameters").get("course_id")

    if week_day == "TOD":
        week_day = get_week_day(0)

    if week_day == "TOM":
        week_day = get_week_day(1)

    if not week_day:
        week_day = req.get("result").get("parameters").get("date")
        if week_day:
            year, month, day = (int(x) for x in week_day.split('-'))    
            ans = datetime.date(year, month, day)
            ans= ans.strftime("%A")
            ans = ans.upper()
            week_day = ans[0:3]

    print (week_day)
    
    # if not week_day:
    #     week_day = get_week_day(0)
    #     if week_day == "SAT" or week_day == "SUN":
    #         out_string += "No classes today! \n This is the time-table for next Monday.\n"
    #         week_day = "MON"

    student_list = {    
        '1338471136207322': '160101076',
        '1653617614727730': '150101031',
        '1852825864791150': '150123004',
    }

    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    roll_no = student_list[sender_id]

    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND course_id =\"" + course_id +"\" AND day = \"" + week_day+ "\" ORDER BY start_time;"

    cursor.execute(query)

    data = cursor.fetchall()
    # data = data[0][0]
    print(data)
    print(len(data))

    for k in data:
        out_string += "You have " + k[0] + " from " + k[1] + " in " + k[2] + "\n"

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

def get_class_timings_nfl(req,res):

    out_string = ""

    nfl = req.get("result").get("parameters").get("time")

    week_day = req.get("result").get("parameters").get("week_day")

    if week_day == "TOD":
        week_day = get_week_day(0)

    if week_day == "TOM":
        week_day = get_week_day(1)

    if not week_day:
        week_day = req.get("result").get("parameters").get("date")
        if week_day:
            year, month, day = (int(x) for x in week_day.split('-'))    
            ans = datetime.date(year, month, day)
            ans= ans.strftime("%A")
            ans = ans.upper()
            week_day = ans[0:3]

    if not week_day:
        week_day = get_week_day(0)
        if week_day == "SAT" or week_day == "SUN":
            out_string += "No classes today! \n This is the time-table for next Monday.\n"
            week_day = "MON"
            nfl = "first"

    student_list = {    
        '1338471136207322': '160101076',
        '1653617614727730': '150101031'
    }

    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    roll_no = student_list[sender_id]
    hour = datetime.datetime.now().hour

    hour = str(hour)
    hour = "{0:0>2}".format(hour)
    hour = hour + ":00:00"

    conn = mysql.connect()
    cursor = conn.cursor()

    if nfl == "first": 
        query = "SELECT course_id, start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND day = \"" + week_day+ "\" ORDER BY start_time LIMIT 1;"
    elif nfl == "last":
        query = "SELECT course_id, start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND day = \"" + week_day+ "\" ORDER BY start_time DESC LIMIT 1;"
    elif nfl == "next":
        query = "SELECT course_id, start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND day = \"" + week_day+ "\" AND start_time > \""+hour+"\"ORDER BY start_time LIMIT 1;"
    elif nfl == "second":
        query = "SELECT course_id, start_time, room_number FROM ( SELECT course_id, start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND day = \"" + week_day+ "\" ORDER BY start_time LIMIT 2) AS alias ORDER BY start_time DESC LIMIT 1;"

    cursor.execute(query)

    data = cursor.fetchall()
    # data = data[0][0]
    print(data)

    temp = data[0]
        # out_list = json.dumps(data)
    out_string += "You have " + temp[0] + " from " + temp[1] + " in " + temp[2] + "\n"

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

def get_location(req,res):

    week_day = get_week_day(0)

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
    if data
        data = data[0]
        # out_list = json.dumps(data)
        out_string = "The Exam is on " + data[0] + " from " + data[1] + " to " + data[2]
    else:
        out_string = "There is no exam for " + course_id +". ENJOY!"

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
