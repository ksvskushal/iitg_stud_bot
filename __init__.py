#!/usr/bin/env python

import urllib
import json
import os


from flask import Flask,request,make_response
from flaskext.mysql import MySQL
import httplib, urllib, json
import os
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
    res = {
    	"speech": "Hello from the other side Bitch !",
        "displayText": "Hello from the other side Bitch !",
        "source": "IITG Student Buddy"
    }
    print request
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print "Starting app on port %d" % port
    app.run(debug=True, port=port, host='0.0.0.0')

def get_latest():

    conn = mysql.connect()
    cursor = conn.cursor()

    query_1 = "SELECT * FROM doc_data ORDER BY id DESC LIMIT 0, 1;"
    cursor.execute(query_1)

    data = cursor.fetchall()

    stri = json.dumps(data)

    return {
        "speech": stri,
        "displayText": stri,
        #"data": {},
        # "contextOut": [],
        "source": "chitra"
    }