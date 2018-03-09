#!/usr/bin/env python
from flask import Flask,request,make_response
from flaskext.mysql import MySQL
import httplib, urllib, json
import os
from collections import defaultdict

mysql= MySQL()

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'EmpData'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    input = json.dumps(req, indent=4)
    if req.get("result").get("action")=="last_visit":
        res = get_latest()
    else:
        res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):

    lst = req.get("originalRequest").get("data").get("message").get("attachments")
    if lst is not None:
        url = lst[0].get("payload").get("url")

    url = str(url)
    word = vision_api(url)
    speech = "This is " + word

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "chitra"
    }

def vision_api(url):
    uri_base = 'westcentralus.api.cognitive.microsoft.com'

    subscription_key = 'da2461a6a46b45d3803aaa0130ba71e3'

    headers = {
        # Request headers.
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subscription_key,
    }

    params = urllib.urlencode({
        # Request parameters. The language setting "unk" means automatically detect the language.
        'language': 'unk',
        'detectOrientation ': 'true',
    })

    # The URL of a JPEG image containing text.
    body = "{'url':" + url + "}" #"{'url': {} }".format(url) #% url
    
    _body = defaultdict(list);
    _body['url'] = url;
    body = str({'url':_body.values()[0]})
    #return body
    
    try:
        # Execute the REST API call and get the response.
        print 'in try'
        conn = httplib.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
        print conn
        conn.request("POST", "/vision/v1.0/ocr?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()

        print data
        # 'data' contains the JSON data. The following formats the JSON data for display.
        parsed = json.loads(data)
        # return json.dumps(parsed)
        #return parsed
        print ("Response:")


        # return (json.dumps(parsed, sort_keys=True, indent=2))


        arr=[]
        
        for obj in parsed['regions']:
            for lines in obj['lines']:
                # print lines
                for wrd in lines['words']:
                    # if('Dr' in wrd['text'] or 'Dr.' in wrd['text']):
                    #    doctor=lines['words']
                    temp=map(int, wrd['boundingBox'].split(','))
                    arr.append(temp)
        maxBoundIndex=-1
        mxBndSize=0
        print 'lund'
        doctor_name=''
      	#  for obj in doctor:
        #    doctor_name=doctor_name+obj['text']+' '
        #print doctor_name
        # print doctor
        # print arr
        # print arr
        # print len(arr)
        # print arr[0][0]

        for i in range(len(arr)):
            print i
            print arr[i][0],arr[i][1],arr[i][2],arr[i][3]
            val=abs(arr[i][0]-arr[i][1])*abs(arr[i][2]-arr[i][3])

            if (val>mxBndSize):
                mxBndSize=val
                print arr[i],val
                maxBoundIndex=i


        print arr[maxBoundIndex]

        arr2=[]
        # time.sleep(30)
        # print 'after time sleep'
        print 'abc'
        j=0;
        for obj in parsed['regions']:
            for lines in obj['lines']:
                for wrd in lines['words']:
                    temp=map(int, wrd['boundingBox'].split(','))
                    if(temp==arr[maxBoundIndex]):
                        print temp
                        print wrd['text']
                        return str(wrd['text'])
                    j=j+1
            # arr.append(temp)

        # return 'dharmesh'
        return json.dumps(parsed)
        mystr=','.join(arr)
        conn.close()


    except Exception as e:
        print('Error:')
        print(e)
        
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


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')


