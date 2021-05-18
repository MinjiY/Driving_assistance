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
from datetime import datetime

import pymysql
import requests


app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.config["DEBUG"] = True


'''
{'date': ['2021-05-12', '2021-05-13', '2021-05-14']}
{'time': ['2:59:28', '0:40:00', '7:21:50']}
{'count': [[3, 2, 2, 3], [1, 3, 1, 2], [7, 4, 3, 2]]}
'''
@app.route('/ajax')
def add_numbers():
    return jsonify(result1="성공", result2="success")

@app.route('/')
def main():
    # 날짜별 총 주행시간
    date_list={
        "date":[]
    }
    time_list={
        "time":[]
    }
    count_list={
        "count":[]
    }
    behavior_list={
        "behavior":[0,0,0,0]
    }
    maxValue = 0
    db = pymysql.connect(host='35.83.241.188', port=3306, db='DRIVINGDB',user='root',passwd='team04')
    cursor = db.cursor()
    sql = 'select Number, driving_date, driving_info, Start_time, End_time, Total_time, Video from driving_dummy order by driving_date asc'
    cursor.execute(sql)
    db.commit()
    result_set = cursor.fetchall()

    for que in result_set:
        dateStr = str(que[1])
            
        if dateStr in date_list["date"]:
            #print(time_list)
            old_time, old_minute, old_second= time_list["time"][-1].split(':')
            new_time, new_minute, new_second= str(que[5]).split(':')
            time = int(old_time)+int(new_time)
            minute= int(old_minute)+int(new_minute)
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
            time, minute, second= str(que[5]).split(':')
            
            que_dict = eval(que[2])
            for stamp in que_dict["driving_info"]:
                st = int(stamp["status"])
                count_list["count"][-1][st] += 1
            
            
            maxValue = max(maxValue,int(time))

    for j in range(4):
        for i in range(len(date_list["date"])):
            behavior_list["behavior"][j] += count_list["count"][i][j]
        

    return render_template('test.html', content_data={"date_list":date_list,"time_list":time_list,"count_list":count_list, "behavior_list":behavior_list})

@app.route('/dashboard')
def dashboard():
    # 날짜별 총 주행시간
    date_list={
        "date":[]
    }
    time_list={
        "time":[]
    }
    count_list={
        "count":[]
    }
    behavior_list={
        "behavior":[0,0,0,0]
    }
    behavior_naming={
        "driving":["정상 주행","졸음 운전","인포테인먼트","휴대폰"]
    }
    maxValue = 0
    db = pymysql.connect(host='35.83.241.188', port=3306, db='DRIVINGDB',user='root',passwd='team04')
    cursor = db.cursor()
    sql = 'select Number, driving_date, driving_info, Start_time, End_time, Total_time, Video from driving_dummy order by driving_date asc'
    cursor.execute(sql)
    db.commit()
    result_set = cursor.fetchall()

    for que in result_set:
        dateStr = str(que[1])
            
        if dateStr in date_list["date"]:
            #print(time_list)
            old_time, old_minute, old_second= time_list["time"][-1].split(':')
            new_time, new_minute, new_second= str(que[5]).split(':')
            time = int(old_time)+int(new_time)
            minute= int(old_minute)+int(new_minute)
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
            time, minute, second= str(que[5]).split(':')
            
            que_dict = eval(que[2])
            for stamp in que_dict["driving_info"]:
                st = int(stamp["status"])
                count_list["count"][-1][st] += 1
            
            
            maxValue = max(maxValue,int(time))

    for j in range(4):
        for i in range(len(date_list["date"])):
            behavior_list["behavior"][j] += count_list["count"][i][j]




    return render_template('main.html', content_data={"date_list":date_list,"time_list":time_list,"count_list":count_list,"behavior_list":behavior_list,"behavior_naming":behavior_naming})
    

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/drivinfo')
def drivinfo():
    

    return render_template('drivinfo.html')

@app.route('/drivscore')
def drivscore():
    return render_template('drivscore.html')




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env.get('PORT', 3000), debug=True)
    #app.run(debug=True)
