#!/usr/bin/env python

import datetime
import calendar
import urllib
import httplib
import json
import time
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

# student_list = {    
#         '1338471136207322': '160101076',
#         '1653617614727730': '150101031',
#         '1852825864791150': '150103085',
#         '1950480881646757': '170106029',
#         '1698196700203262': '150108045'
#     }

@app.route("/complexshit")
def hello():
    return "Hello, I love Digital Ocean!"

@app.route("/PrivacyPolicy")
def privacy():
    return "<br><br>This is a project by the students of IITG coding club.<br>No data is collected or sold by the usage of this application.<br>P.S. Please accept our policy, we have to submit the project tomorrow"


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

    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    if intent_name == "register":
        res = register(req,res)
    elif intent_name == "delete":
        res = delete(req,res)

    if get_roll_number(sender_id) == "":

        out_string = "You're not registered.\nPlease register by using command\n"
        out_string+= "Register <Roll_number>\n Example: register 150101001"

        return {
            "speech": out_string,
            "displayText": out_string,
            #"data": {},
            # "contextOut": [],
            "source": "IITG-Student-Buddy"
        }

    elif intent_name == "specific-course-location":
        res = get_location(req,res)
    elif intent_name == "exam-timings":
        res = get_exam_timings(req,res)
    elif intent_name == "timings-nfl-class":
        res = get_class_timings_nfl(req,res)
    elif intent_name == "schedule-specific-day":
        res = get_schedule_specific_day(req,res)
    elif intent_name == "specific-course-nfl":
        res = get_specific_course_nfl(req,res)
    elif intent_name == "bus-timings":
        res = get_bus_timings(req,res)
    elif intent_name == "my-ip-hostel":
        res = get_hostel(req,res)

    print("Response:")
    res = json.dumps(res, indent=4)
    print (res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def check_if_valid_roll(roll_number):
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT roll_number FROM cwsl WHERE roll_number = " + roll_number + ";"

    cursor.execute(query)

    data = cursor.fetchall()

    if len(data) == 0:
        return "INVALID"
    else:
        return "VALID"

def register(req,res):

    out_string = ""

    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    roll_number = req.get("result").get("parameters").get("course_id")

    validity = check_if_valid_roll(roll_number)

    if validity == "INVALID":

        out_string += "Enter a valid ID number. Try again"

        return {
            "speech": out_string,
            "displayText": out_string,
            #"data": {},
            # "contextOut": [],
            "source": "IITG-Student-Buddy"
        }

    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT roll_number FROM student_list WHERE facebook_id = " + sender_id + ";"

    cursor.execute(query)

    data = cursor.fetchall()

    if len(data) != 0:

        out_string += "This Facebook ID is already registered to the roll number " + data[0] + "\n"
        out_string += "To change the roll number, first delete the previous entry and then register. \n"
        out_string += "To delete use the command Delete <Roll Number> Ex: Delete 150101001"

        return {
            "speech": out_string,
            "displayText": out_string,
            #"data": {},
            # "contextOut": [],
            "source": "IITG-Student-Buddy"
        }

    conn_2 = mysql.connect()
    cursor_2 = conn_2.cursor()

    query_2 = "INSERT INTO student_list VALUES (" + roll_number + "," + sender_id + ");"

    cursor_2.execute(query_2)

    out_string += "Successfully Registered.\nHi, I am Student Buddy.\n Your Virtual Assistant in campus\n"
    out_string += "We are in Beta right now. \nPlese give feedback by sending a message to Kushal K S V S\n"

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

def delete(req,res):

    out_string = ""

    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    roll_number = req.get("result").get("parameters").get("course_id")

    validity = check_if_valid_roll(roll_number)

    if validity == "INVALID":

        out_string += "Enter a valid ID number. Try again"

        return {
            "speech": out_string,
            "displayText": out_string,
            #"data": {},
            # "contextOut": [],
            "source": "IITG-Student-Buddy"
        }

    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT roll_number FROM student_list WHERE facebook_id = " + sender_id + " AND roll_number = " + roll_number + ";"

    cursor.execute(query)

    data = cursor.fetchall()

    if len(data) == 0:

        out_string += "Not Permitted. Use the ID registered with this Facebook Account\n"

        return {
            "speech": out_string,
            "displayText": out_string,
            #"data": {},
            # "contextOut": [],
            "source": "IITG-Student-Buddy"
        }

    conn_2 = mysql.connect()
    cursor_2 = conn_2.cursor()

    query_2 = "DELETE FROM student_list WHERE facebook_id = " + sender_id + ";"

    cursor_2.execute(query_2)

    out_string += "Successfully Deleted.\n"
    out_string += "To register, Type Register <Roll Number>\n"
    out_string += "We are in Beta right now. \nPlese give feedback by sending a message to Kushal K S V S\n"

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

def get_roll_number(sender_id):

    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT roll_number FROM student_list WHERE facebook_id = " + sender_id + ";"

    cursor.execute(query)

    data = cursor.fetchall()

    print (data) # debugging

    return data

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
        print (week_day) # to debug
        if week_day == "SAT" or week_day == "SUN":
            out_string += "No classes today! \n This is the time-table for next Monday.\n"
            week_day = "MON"
            print (week_day) #to debug 


    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    roll_no = get_roll_number(sender_id)

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

def get_specific_course_nfl(req,res):

    out_string = ""

    nfl = req.get("result").get("parameters").get("time")
    course_id = req.get("result").get("parameters").get("course_id")

    week_day = req.get("result").get("parameters").get("week_day")

    if not nfl and not week_day:
        nfl = "first"

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
            # out_string += "No classes today! \n This is the time-table for next Monday.\n"
            week_day = "MON"
            nfl = "first"


    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    roll_no = get_roll_number(sender_id)

    hour = datetime.datetime.now().hour

    hour = str(hour)
    hour = "{0:0>2}".format(hour)
    hour = hour + ":00:00"

    conn = mysql.connect()
    cursor = conn.cursor()

    if nfl == "first": 
        query = "SELECT start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND course_id = \"" + course_id + "\" AND day = \"" + week_day+ "\" ORDER BY start_time LIMIT 1;"
    elif nfl == "last":
        query = "SELECT start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND course_id = \"" + course_id + "\" AND day = \"" + week_day+ "\" ORDER BY start_time DESC LIMIT 1;"
    elif nfl == "next":
        query = "SELECT start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND course_id = \"" + course_id + "\" AND day = \"" + week_day+ "\" AND start_time > \""+hour+"\"ORDER BY start_time LIMIT 1;"
    elif nfl == "second":
        query = "SELECT start_time, room_number FROM ( SELECT course_id, start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND day = \"" + week_day+ "\" ORDER BY start_time LIMIT 2) AS alias ORDER BY start_time DESC LIMIT 1;"
    else:
        query = "SELECT start_time, room_number FROM ctt WHERE roll_number = " + roll_no + " AND course_id = \"" + course_id + "\" AND day = \"" + week_day+ "\";"

    cursor.execute(query)

    data = cursor.fetchall()
    # data = data[0][0]
    print(data)
    print(len(data))

    for k in data:
        out_string += "You have " + course_id + " from " + k[0] + " in " + k[1] + " on "+ week_day + "\n"
    
    if not data:
        out_string = "You don't have any class on" + week_day

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

    

    sender_id = req.get("originalRequest").get("data").get("sender").get("id")

    roll_no = get_roll_number(sender_id)

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

    out_string = ""

    query = "SELECT room_number FROM ScheduledIn WHERE course_id = \"" + course_id + "\" AND day = \"" + week_day + "\";"

    if week_day == "SAT" or week_day == "SUN":
        query = "SELECT day,room_number FROM ScheduledIn WHERE course_id = \"" + course_id + "\";"

    cursor.execute(query)

    data = cursor.fetchall()

    if week_day == "SAT" or week_day == "SUN":
        out_string+= "Day  Room\n"
        for x in data:
            out_string+= x[0] + "  - " + x[1] + "\n"
    else:
        data = data[0]
        out_string = json.dumps(data)
        out_string += "The Class is in " + out_string

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

def get_bus_timings(req,res):
    
    now = datetime.datetime.now()
    print(now)
    sch = req.get("result").get("parameters").get("schedule")
    city = req.get("result").get("parameters").get("city")
    
    # now -= time.timedelta(seconds=19800)
    
    if sch:
        out_string = "The bus timings are:\n\nFrom City\n6:45 AM, 7:45AM, 8:15 AM, 10:00AM, 11:00 AM, 01:00PM, 2:00PM, 3:00PM, 4:00PM, 5:00, 6:00, 6:30PM, 7:15PM, 8:00PM, 8:30PM, 8:45PM, 8:55PM, 9:00PM"
        out_string += "\n\nTo City\n8:00AM, 9:00AM, 10:00AM, 10:30AM, 12:00, 01:00PM, 2:00PM, 3:00PM, 3:30PM, 4:00PM, 5:00, 5:40, 6:45PM, 8:00PM, 8:40PM, 9:00PM, 9:15PM, 9:30PM"
    elif city == "from-city":
        if now.hour < 6 and now.minute < 45:
            out_string = "The next bus is at 6:45AM"
        elif now.hour < 7 and now.minute < 45:
            out_string = "The next bus is at 7:45AM"
        elif now.hour < 8 and now.minute < 15:
            out_string = "The next bus is at 8:15AM"
        elif now.hour < 10 and now.minute < 00:
            out_string = "The next bus is at 10:00AM"
        elif now.hour < 11 and now.minute < 0:
            out_string = "The next bus is at 11:00AM"
        elif now.hour < 1+12 and now.minute < 0:
            out_string = "The next bus is at 1:00PM"
        elif now.hour < 2+12 and now.minute < 00:
            out_string = "The next bus is at 2:00PM"
        elif now.hour < 3+12 and now.minute < 0:
            out_string = "The next bus is at 3:00PM"
        elif now.hour < 4+12 and now.minute < 00:
            out_string = "The next bus is at 4:00PM"
        elif now.hour < 5+12 and now.minute < 00:
            out_string = "The next bus is at 5:00PM"
        elif now.hour < 6+12 and now.minute < 0:
            out_string = "The next bus is at 6:00PM"
        elif now.hour < 6+12 and now.minute < 30:
            out_string = "The next bus is at 6:30PM"
        elif now.hour < 7+12 and now.minute < 15:
            out_string = "The next bus is at 7:15PM"
        elif now.hour < 8+12 and now.minute < 45:
            out_string = "The next bus is at 8:45PM"

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

    # print("sem is " + sem)
    if sem == "midsem":
        query = "SELECT exam_date,start_time,end_time FROM mid_ett WHERE course_id = \"" + course_id + "\";"
    elif sem == "endsem":
        query = "SELECT exam_date,start_time,end_time FROM end_ett WHERE course_id = \"" + course_id + "\";"
    elif sem ==  "" or sem == None:
        if now < betw_mid_end:
            query = "SELECT exam_date,start_time,end_time FROM mid_ett WHERE course_id = \"" + course_id + "\";"
        else:
            query = "SELECT exam_date,start_time,end_time FROM end_ett WHERE course_id = \"" + course_id + "\";"

    cursor.execute(query)

    data = cursor.fetchall()
    # data = data[0][0]
    print(data)
    if data:
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

def get_hostel(req,res):

    info = req.get("result").get("parameters").get("hostel")
    info = info.replace("."," ")
    info = info.replace("-"," ")
    info = info.split()

    hostel = info[0]
    hostel = hostel[0:3]
    hostel = hostel.upper()

    block = 0
    if len(info) is 3:
        block = info[1][0]
        block = block.upper()
        block = ord(block) - 65

    block = str(block)

    l = len(info)

    room = info[l - 1]
    room = int(room)
    room = "{0:0=3d}".format(room)
    room = str(room)
    floor = room[0]
    room = room[1:]
    room = str(int(room))


    hostel_dict = {
    'BAR' : ['255.255.192.0' , '10.10.0.254'],
    'BRA' : ['255.255.192.0' , '10.12.0.254'],
    'DIB' : ['255.255.192.0' , '10.8.0.254'],
    'DIH' : ['255.255.252.0' , '10.0.0.254'],
    'KAM' : ['255.255.192.0' , '10.9.0.254'],
    'KAP' : ['255.255.252.0' , '10.1.0.254'],
    'MAN' : ['255.255.192.0' , '10.4.0.254'],
    'MAR' : ['255.255.252.0' , '10.17.0.254'],
    'SIA' : ['255.255.252.0' , '10.3.0.254'],
    'SUB' : ['255.255.192.0' , '10.16.0.254'],
    'UMI' : ['255.255.192.0' , '10.11.0.254']}

    prefix = hostel_dict[hostel][1]
    prefix = prefix.split(".")

    a = prefix[0]
    b = prefix[1]
    c = block + floor
    c = str(int(c))
    d = room

    ip = ".".join([a,b,c,d])

    out_string = "IP address - " + ip + "\n"
    out_string += "Subnet - " + hostel_dict[hostel][0] + "\n"
    out_string += "Gateway - " + hostel_dict[hostel][1]

    return {
        "speech": out_string,
        "displayText": out_string,
        #"data": {},
        # "contextOut": [],
        "source": "IITG-Student-Buddy"
    }

if __name__ == "__main__":
    # port = int(os.getenv('PORT', 80))
    # print "Starting app on port %d" % port
    app.run(debug=True)
