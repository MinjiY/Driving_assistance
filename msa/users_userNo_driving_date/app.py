from flask import Flask, jsonify
import flask_restful
from flask_restful import reqparse
import pymysql
from config import db_config
from os import environ as env
import copy

app = Flask(__name__)
app.config["DEBUG"] = True
api = flask_restful.Api(app)


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

class userDrivinginfo_drivingDate(flask_restful.Resource):
    def __init__(self):
        config = db_config()
        self.db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'], passwd=config['passwd'], db=config['db'], charset='utf8')
        self.cursor = self.db.cursor()
        
    def get(self,user_no):
        query = 'select driving_date, Start_time, End_time from driving_dummy where number=%s order by driving_date asc'
    
        self.cursor.execute(query, user_no)
        self.db.commit()
        result_set = self.cursor.fetchall()
        self.db.close()
        
        day_list=[]
        driving_list = []
        temp_list = []
        for data in result_set:
            if data[0] not in day_list:
                day_list.append(str(data[0]))
                if len(day_list) > 1:
                    driving_list.append(copy.deepcopy(temp_list))
                    temp_list.clear()
            temp_list.append( {"start": str(data[1]).split()[1], "end": str(data[2]).split()[1] } )
        driving_list.append(temp_list)

        json_data={"day_list":day_list, "driving_list":driving_list}

        response =jsonify(json_data)
        response.status_code = 200
        return response
        

class userDrivinginfo_drivingDateDetail(flask_restful.Resource):
    def __init__(self):
        config = db_config()
        self.db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'], passwd=config['passwd'], db=config['db'], charset='utf8')
        self.cursor = self.db.cursor()
        
    def get(self,user_no,drivingDate,start):
        query = 'select Number, driving_date, driving_info, Start_time, End_time, Total_time, Video from driving_dummy where driving_date=%s and Start_time=%s and number=%s'
        self.cursor.execute(query,(drivingDate,drivingDate+' '+start,user_no))
        self.db.commit()
        result_set = self.cursor.fetchall()
        self.db.close()

        # driving_info 추출
        driving_info =eval(result_set[0][2])
   
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

        json_data = {"driving_date":str(result_set[0][1]), "start_time":str(result_set[0][3]), "End_time": str(result_set[0][4]),"videoSrc": str(result_set[0][6]), "count_data" :count_data[0], "total_time": total_time[0], "driving_info":driving_info}


        response =jsonify(json_data)
        response.status_code = 200
        return response

    
api.add_resource(userDrivinginfo_drivingDate, '/users/<int:user_no>/driving/dates')
api.add_resource(userDrivinginfo_drivingDateDetail, '/users/<int:user_no>/driving/dates/<string:drivingDate>/<string:start>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=env.get('PORT', 5002), debug=True)