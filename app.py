from flask import Flask, jsonify, request, redirect, url_for, _request_ctx_stack
import requests
import random
import string
import sqlite3 as sql

app = Flask(__name__)
@app.route("/")
def index1():
  return """Use http://urrl.herokuapp.com/gen/?url={your_url} to generate url"""

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
  ip_url = "http://ip-api.com/json/"+ ip[0]['ip'].split(",")[0]
  ip_info = requests.get(ip_url)
  result = {"ip":ip[0]['ip'], "ip_info": ip_info.text, "family":family, "device": device, "os":os, "platform":platform, "browser":browser, "version":version, "user_agent":usr_agnt}
  a = abbr
  with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("UPDATE iplogger SET track=? where abbr=?",(str(result),str(a)))
    con.commit()
  with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute('SELECT url FROM iplogger where abbr=?',[a])
    link = cur.fetchall();
    con.commit()
    link1 = str(link[0][0])
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
    tra = "None"
    with sql.connect("database.db") as con:
      cur = con.cursor()
      cur.execute("INSERT INTO iplogger (url,shrturl,abbr,track) VALUES (?,?,?,?)",(url,shrt,result_str,tra))
      con.commit()
    result = {"url":"http://urrl.herokuapp.com/" + result_str}
    return jsonify(result)
   
@app.route('/track/<string:abbr>', methods=['GET'])
def get_tasks(abbr):
    a = abbr
    with sql.connect("database.db") as con:
      cur = con.cursor()
      cur.execute('SELECT track FROM iplogger where abbr=?',[a])
      link = cur.fetchall();
      con.commit()
      result = str(link[0][0])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000,use_reloader=True,threaded=True)