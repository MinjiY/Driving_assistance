from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import request
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from dotenv import load_dotenv, find_dotenv
import constants
from flask_paginate import Pagination, get_page_parameter
import pymysql
import requests
from flask import Blueprint
import math
from config import db_config
import copy

# Auth0 login
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.config['JSON_AS_ASCII'] = False

app.secret_key = constants.SECRET_KEY
app.debug = True


def cal_totalTime(endTime, startTime):
    et = endTime.split()[1].split(':')
    st = startTime.split()[1].split(':')

    if len(et) == 2:
        tet = int(et[0])*60 + int(et[1])
        tst = int(st[0])*60 + int(st[1])
        f = tet - tst

        temp = str(f//60) + ':' + str(f % 60)
    elif len(et) == 3:
        tet = int(et[0])*3600 + int(et[1])*60 + int(et[2])
        tst = int(st[0])*3600 + int(st[1])*60 + int(st[2])
        f = tet-tst

        temp = str(f//3600)+':' + str((f % 3600)//60)+':'+str((f % 3600) % 60)

    return temp


# DB
config = db_config()
db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'],
                     passwd=config['passwd'], db=config['db'], charset='utf8')
cursor = db.cursor()


@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


# Controllers API

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/callback')
def callback_handling():
    tck = auth0.authorize_access_token()
    print("token = ", tck)
    resp = auth0.get('userinfo')

    userinfo = resp.json()

    session[constants.JWT_PAYLOAD] = userinfo
    print("userinfo = ", userinfo)
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture'],
    }

    # userinfo DB 저장
    try:
        query = """insert into user (id, name, picture) values (%s, %s, %s)"""
        cursor.execute(
            query, (userinfo['sub'], userinfo['name'], userinfo['picture']))
        db.commit()
        db.close()
    except:
        pass
    try:
        query = """select Number from user where name=%s"""
        cursor.execute(
            query, (userinfo['name']))
        row = cursor.fetchone()
        global user_no
        user_no = row[0]
    except:
        pass

    if userinfo['name'] == 'admin@admin.com':
        return redirect('/admin/users')

    return redirect('/main')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for(
        'home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/main')
def main():
    # 날짜별 총 주행시간
    date_list = {
        "date": []
    }
    time_list = {
        "time": []
    }
    count_list = {
        "count": []
    }
    behavior_list = {
        "behavior": [0, 0, 0, 0]
    }
    behavior_naming = {
        "driving": ["정상 주행", "졸음 운전", "인포테인먼트", "휴대폰"]
    }
    maxValue = 0
    db = pymysql.connect(host='35.83.241.188', port=3306,
                         db='DRIVINGDB', user='root', passwd='team04')
    cursor = db.cursor()
    sql = 'select Number, driving_date, driving_info, Start_time, End_time, Total_time, Video from driving_dummy order by driving_date asc'
    cursor.execute(sql)
    db.commit()
    result_set = cursor.fetchall()

    for que in result_set:
        dateStr = str(que[1])

        if dateStr in date_list["date"]:
            # print(time_list)
            old_time, old_minute, old_second = time_list["time"][-1].split(':')
            new_time, new_minute, new_second = str(que[5]).split(':')
            time = int(old_time)+int(new_time)
            minute = int(old_minute)+int(new_minute)
            second = int(old_second)+int(new_second)
            time_list["time"][-1] = str(time)+':'+str(minute)+':'+str(second)

            que_dict = eval(que[2])
            for stamp in que_dict["driving_info"]:
                st = int(stamp["status"])
                cnt = count_list["count"][-1][st]
                count_list["count"][-1][st] = cnt+1

        else:
            date_list["date"].append(dateStr)
            time_list["time"].append(str(que[5]))
            count_list["count"].append([0, 0, 0, 0])
            time, minute, second = str(que[5]).split(':')

            que_dict = eval(que[2])
            for stamp in que_dict["driving_info"]:
                st = int(stamp["status"])
                count_list["count"][-1][st] += 1

            maxValue = max(maxValue, int(time))

    for j in range(4):
        for i in range(len(date_list["date"])):
            behavior_list["behavior"][j] += count_list["count"][i][j]

    # 운전 점수 계산
    try:
        score = 100
        sleep = 0
        for i in count_list['count']:
            sleep += i[1]
        score = score - (sleep * 2)
        print(score)
        db = pymysql.connect(host='35.83.241.188', port=3306,
                            db='DRIVINGDB', user='root', passwd='team04')
        cursor = db.cursor()
        sql = 'UPDATE user SET driving_score=%s WHERE Number=%s'
        cursor.execute(sql, (score, user_no))
        db.commit()
    except:
        pass
    global content_data
    content_data = {"date_list": date_list, "time_list": time_list, "count_list": count_list, "behavior_list": behavior_list, "behavior_naming": behavior_naming}
    

    return render_template('main.html', userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4), content_data={"date_list": date_list, "time_list": time_list, "count_list": count_list, "behavior_list": behavior_list, "behavior_naming": behavior_naming})


@app.route('/profile')
def profile():
    return render_template('profile.html', userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))


@app.route('/drivingInfo', methods=['GET'])
def drivingInfo():
    day_list=[]
    driving_list = []
    db = pymysql.connect(host='35.83.241.188', port=3306, db='DRIVINGDB', user='root', passwd='team04')
    cursor = db.cursor()
    sql = 'select driving_date, Start_time, End_time from driving_dummy order by driving_date asc'
    cursor.execute(sql)
    db.commit()
    result_set = cursor.fetchall()
    db.close()
    
    temp_list = []
    for data in result_set:
        if data[0] not in day_list:
            day_list.append(data[0])
            if len(day_list) > 1:
                driving_list.append(copy.deepcopy(temp_list))
                temp_list.clear()
        temp_list.append( {"start": str(data[1]).split()[1], "end": str(data[2]).split()[1]} )
    driving_list.append(temp_list)
    
    
    return render_template('drivingInfo.html', userinfo=session[constants.PROFILE_KEY], userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4),content_data={"day_list":day_list, "driving_list":driving_list})

@app.route('/drivingInfo_detail/<string:drivingDate>/<string:start>')
def drivingInfo_detail(drivingDate,start):
    db = pymysql.connect(host='35.83.241.188', port=3306, db='DRIVINGDB', user='root', passwd='team04')

    cursor = db.cursor()
    sql = 'select Number, driving_date, driving_info, Start_time, End_time, Total_time, Video from driving_dummy where driving_date=%s and Start_time=%s'

    cursor.execute(sql,(drivingDate,drivingDate+' '+start))
    db.commit()
    result_set = cursor.fetchall()
    db.close()


    # driving_info 추출
    json_data =eval(result_set[0][2])
   
    # 총 분류 행동 횟수 추출
    count_data = []
    total_time = []
    
    for i in range(len(result_set)):
        dict_data = eval(result_set[i][2])
        status_list=[0,0,0,0]
        time_list=[]
        for j in dict_data["driving_info"]:
            status_list[int(j["status"])] +=1
            time_list.append(cal_totalTime(j["EndTime"] , j["startTime"]))
        count_data.append(status_list)
        total_time.append(time_list)



    return render_template('drivingInfo_detail.html',userinfo=session[constants.PROFILE_KEY],userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4),driving_date=result_set[0][1],start_time=result_set[0][3], End_time=result_set[0][4], videoSrc=result_set[0][6],count_data=count_data[0], total_time=total_time[0],json_data=json_data)



@app.route('/drivingScore')
def drivingScore():
    userinfo = session[constants.PROFILE_KEY]
    query = "SELECT driving_score FROM user WHERE id=%s"
    cursor.execute(query, (userinfo['user_id']))
    db.commit()
    score = cursor.fetchone()
    print(score)
    print(content_data)

    return render_template('drivingScore.html', userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4), score=score, content_data=content_data)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404





### admin

@app.route('/admin/users')
def users():
    db = pymysql.connect(host='35.83.241.188', port=3306, db='DRIVINGDB', user='root', passwd='team04')
    cursor = db.cursor()
    sql = 'select name, picture, created_at, driving_score, number from user where name not like "%admin%"'
    cursor.execute(sql)
    db.commit()
    result_set = cursor.fetchall()
    db.close()

    return render_template('userListView.html', userinfo=session[constants.PROFILE_KEY], userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4), datas=result_set)


@app.route('/admin/users/<int:number>')
def userDetail(number):
    date_list = {
        "date": []
    }
    time_list = {
        "time": []
    }
    count_list = {
        "count": []
    }
    behavior_list = {
        "behavior": [0, 0, 0, 0]
    }
    behavior_naming = {
        "driving": ["정상 주행", "졸음 운전", "인포테인먼트", "휴대폰"]
    }
    maxValue = 0
    config = db_config()
    db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'],
                     passwd=config['passwd'], db=config['db'], charset='utf8')
    cursor = db.cursor()
    sql = 'select Number, driving_date, driving_info, Start_time, End_time, Total_time, Video from driving_dummy where Number=%s order by driving_date asc'
    cursor.execute(sql,number)
    db.commit()
    result_set = cursor.fetchall()

    sql = 'select name from user where number=%s'
    cursor.execute(sql,number)
    db.commit()
    user_name_query = cursor.fetchall()
    db.close()
    user_name=user_name_query[0][0]
    print(user_name)

    for que in result_set:
        dateStr = str(que[1])

        if dateStr in date_list["date"]:
            # print(time_list)
            old_time, old_minute, old_second = time_list["time"][-1].split(':')
            new_time, new_minute, new_second = str(que[5]).split(':')
            time = int(old_time)+int(new_time)
            minute = int(old_minute)+int(new_minute)
            second = int(old_second)+int(new_second)
            time_list["time"][-1] = str(time)+':'+str(minute)+':'+str(second)

            que_dict = eval(que[2])
            for stamp in que_dict["driving_info"]:
                st = int(stamp["status"])
                cnt = count_list["count"][-1][st]
                count_list["count"][-1][st] = cnt+1

        else:
            date_list["date"].append(dateStr)
            time_list["time"].append(str(que[5]))
            count_list["count"].append([0, 0, 0, 0])
            time, minute, second = str(que[5]).split(':')

            que_dict = eval(que[2])
            for stamp in que_dict["driving_info"]:
                st = int(stamp["status"])
                count_list["count"][-1][st] += 1

            maxValue = max(maxValue, int(time))

    for j in range(4):
        for i in range(len(date_list["date"])):
            behavior_list["behavior"][j] += count_list["count"][i][j]

    return render_template('userDetailView.html', userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4), content_data={"date_list": date_list, "time_list": time_list, "count_list": count_list, "behavior_list": behavior_list, "behavior_naming": behavior_naming}, user_name=user_name)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=env.get('PORT', 3000), debug=True)
    # app.run(debug=True)
