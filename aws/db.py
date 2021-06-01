import pymysql
import json
number = 1

driving_date = '2021-05-20'

test = { 
    "driving_info":[
        { "status": "0", "startTime": "09:00:00", "EndTime": "09:00:20"},
        { "status": "1", "startTime": "09:00:20", "EndTime": "09:00:38"},
        { "status": "0", "startTime": "09:00:38", "EndTime": "09:01:05"}
    ]
}

driving_info = json.dumps(test)

Start_time = '2021-05-20 09:00:00'
End_time = '2021-05-20 09:01:05'
Total_time = '0:01:05'


Video= 'https://yangjae-team04-s3.s3-us-west-2.amazonaws.com/user1/team04-test6.mp4'

db = pymysql.connect(host='', port=3306, user='root',
                        passwd='team04', db='DRIVINGDB', charset='utf8')                     


cursor = db.cursor()
query = """INSERT INTO driving_dummy VALUES (%s, %s, %s, %s, %s, %s, %s);"""
cursor.execute(query, (number, driving_date, driving_info, Start_time, End_time, Total_time, Video))
db.commit()
db.close()