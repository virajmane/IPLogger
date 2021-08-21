from flask import Flask, jsonify, request, redirect, url_for, _request_ctx_stack, render_template
import requests
import random
import string
import pyrebase
import os

conf = {
    "apiKey": os.environ.get('apiKey'),
    "authDomain": os.environ.get('authDomain'),
    "databaseURL": os.environ.get('databaseURL'),
    "projectId": os.environ.get('projectId'),
    "storageBucket": os.environ.get('storageBucket'),
    "messagingSenderId": os.environ.get('messagingSenderId'),
    "appId": os.environ.get('appId'),
    "measurementId": os.environ.get('measurementId')
  }
firebase = pyrebase.initialize_app(conf)
db = firebase.database()

app = Flask(__name__)
@app.route("/", methods=["GET","POST"])
def index1():
  if request.method=="GET":
    return render_template("index.html")
  else:
    url = request.form["url"]
    return redirect(f"http://urrl.herokuapp.com/gen/?url={url}")

@app.route("/<string:abbr>/")
def index(abbr):
  if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
      ip = {'ip': request.environ['REMOTE_ADDR']}, 200
  else:
      ip = {'ip': request.environ['HTTP_X_FORWARDED_FOR']}, 200
  user_agent = request.user_agent
  platform = user_agent.platform
  browser = user_agent.browser
  version = user_agent.version
  usr_agnt = user_agent.string
  family = usr_agnt.split("(")[1].split(")")[0].split(";")[0]
  os = usr_agnt.split("(")[1].split(")")[0].split(";")[1]
  device = usr_agnt.split("(")[1].split(")")[0].split(";")[2]
  ip_url = "http://ip-api.com/json/"+ ip[0]['ip'].split(",")[0]+ "?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
  ip_info = requests.get(ip_url).json()
  result = {"ip":ip[0]['ip'], "ip_info": ip_info, "family":family, "device": device, "os":os, "platform":platform, "browser":browser, "version":version, "user_agent":usr_agnt}
  a = abbr
  db.child(a).update({"track": result})
  user = db.child(a).get()
  link1 = user.val()["original_url"]
  if "http" not in link1:
    final = "https://"+str(link1)
  else:
    final = link1
  return redirect(final)

@app.route("/gen/")
def shrtn():
    url = request.args.get("url")
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(5)))
    shrt = "http://urrl.herokuapp.com/" + result_str
    tra = "No one has accessed the link yet"
    data = { "id": result_str, "original_url": url, "shortened_url":shrt, "track":tra}
    
    db.child(result_str).set(data)
    shrt_url = "http://urrl.herokuapp.com/" + result_str
    track_url = "http://urrl.herokuapp.com/track/" + result_str
    return render_template('generate.html', shrt_url = shrt_url, track_url = track_url)
   
@app.route('/track/<string:abbr>', methods=['GET'])
def get_tasks(abbr):
    a = abbr
    user = db.child(a).get()
    return jsonify(user.val()["track"])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000,use_reloader=True,threaded=True)
