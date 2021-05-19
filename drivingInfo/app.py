from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template, request
from flask import session
from flask import url_for
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter
import pymysql
import requests
from flask import Blueprint
import math


app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.config["DEBUG"] = True



def cal_totalTime(endTime, startTime):
    et = endTime.split()[1].split(':')
    st = startTime.split()[1].split(':')
    
    if len(et) == 2:
        tet = int(et[0])*60 + int(et[1])
        tst = int(st[0])*60 + int(st[1])
        f = tet - tst

        temp = str(f//60) +':'+ str(f%60)
    elif len(et) == 3:
        tet= int(et[0])*3600 +int(et[1])*60 +int(et[2])
        tst= int(st[0])*3600 +int(st[1])*60 +int(st[2])
        f = tet-tst

        temp = str(f//3600)+':'+ str((f%3600)//60)+':'+str((f%3600)%60)
    

    return temp



@app.route('/')
def index():
    

    return render_template('test.html')

@app.route('/main')
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


@app.route('/drivingInfo', methods=['GET','POST'] )
def drivingInfo():

    db = pymysql.connect(host='35.83.241.188', port=3306, db='DRIVINGDB',user='root',passwd='team04')
    cursor = db.cursor()
    _toDay = '2021-05-12'
        
    if (request.method == 'POST'):
        value = request.form['calendar']
        _toDay=value

    sql = 'select Number, driving_date, driving_info, Start_time, End_time, Total_time, Video from driving_dummy where driving_date=%s'
    cursor.execute(sql,(_toDay))
    db.commit()
    result_set = cursor.fetchall()
    page = request.args.get("page", 1, type=int)
    limit = 1

    tot_count= len(result_set)
    
    last_page_num = math.ceil(tot_count / limit) 
    block_size = 1
    block_num = int((page - 1) / block_size)
    block_start = (block_size * block_num) + 1
    block_end = block_start + (block_size - 1)

    # driving_info 추출
    json_data =[]
    for i in range(len(result_set)):
        json_data.append(eval(result_set[i][2]))
    
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
    

    return render_template(
        "drivingInfo.html",
        datas=result_set,
        json_data=json_data,
        count_data=count_data,
        _toDay=_toDay,
        total_time=total_time,
        limit=limit,
        page=page,
        block_start=block_start,
        block_end=block_end,
        last_page_num=last_page_num)


@app.route('/drivscore')
def drivscore():
    return render_template('drivscore.html')




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env.get('PORT', 3000), debug=True)
    #app.run(debug=True)
