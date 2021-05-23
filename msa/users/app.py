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

class users_info(flask_restful.Resource):
    def __init__(self):
        config = db_config()
        self.db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'], passwd=config['passwd'], db=config['db'], charset='utf8')
        self.cursor = self.db.cursor()
        
    
    def get(self):
        sql = 'select name, picture, created_at, driving_score, number from user where name not like "%admin%"'
        self.cursor.execute(sql)
        self.db.commit()
        result_set = self.cursor.fetchall()
        self.db.close()
        
        user_list=[]
        user_info=[]
        for user in result_set:
            for info in user:
                user_info.append(str(info))
            user_list.append(copy.deepcopy(user_info))
            user_info.clear()
        response =jsonify(user_list)
        response.status_code = 200
        return response
        

class users_infoDetail(flask_restful.Resource):
    def __init__(self):
        config = db_config()
        self.db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'], passwd=config['passwd'], db=config['db'], charset='utf8')
        
        self.cursor = self.db.cursor()
        
    
    def get(self,user_no):
        sql = 'select name, picture, created_at, driving_score from user where number=%s'
        self.cursor.execute(sql,user_no)
        self.db.commit()
        result_set = self.cursor.fetchone()
        self.db.close()
        
        user_info = {"name": result_set[0], "picture":str(result_set[1]), "created_at":str(result_set[2]), "driving_score":result_set[3]}

        response =jsonify(user_info)
        response.status_code = 200
        return response

api.add_resource(users_info, '/users')
api.add_resource(users_infoDetail, '/users/<int:user_no>')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=env.get('PORT', 5003), debug=True)