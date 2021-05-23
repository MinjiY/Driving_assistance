from flask import Flask, jsonify
import flask_restful
from flask_restful import reqparse
import pymysql
from config import db_config
from os import environ as env


app = Flask(__name__)
app.config["DEBUG"] = True
api = flask_restful.Api(app)

class userDrivinginfo_totalcal(flask_restful.Resource):
    def __init__(self):
        config = db_config()
        self.db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'], passwd=config['passwd'], db=config['db'], charset='utf8')
        self.cursor = self.db.cursor()
        
    
    def get(self,user_no):
        # 날짜별 총 주행시간
        date_list = { "date": [] }
        time_list = { "time": [] }
        count_list = { "count": [] }
        behavior_list = { "behavior": [0, 0, 0, 0] }
        query = 'select Number, driving_date, driving_info, Start_time, End_time, Total_time from driving_dummy where number=%s order by driving_date asc'
        self.cursor.execute(query,user_no)
        self.db.commit()
        result_set = self.cursor.fetchall()

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


        for j in range(4):
            for i in range(len(date_list["date"])):
                behavior_list["behavior"][j] += count_list["count"][i][j]

        json_data={"date_list": date_list, "time_list": time_list, "count_list": count_list, "behavior_list": behavior_list}

        try:
            score = 100
            sleep = 0
            for i in count_list['count']:
                sleep += i[1]
                score = score - (sleep * 2)
            sql = 'UPDATE user SET driving_score=%s WHERE Number=%s'
            self.cursor.execute(sql, (score, user_no))
            self.db.commit()
        except:
            pass

        self.db.close()
        response =jsonify(json_data)
        response.status_code = 200
        return response
        
    

api.add_resource(userDrivinginfo_totalcal, '/users/<int:user_no>/driving')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=env.get('PORT', 5000), debug=True)