#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)
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

