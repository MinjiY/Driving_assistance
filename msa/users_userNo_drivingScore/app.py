from flask import Flask, jsonify
import flask_restful
from flask_restful import reqparse
import pymysql
from config import db_config
from os import environ as env


app = Flask(__name__)
app.config["DEBUG"] = True
api = flask_restful.Api(app)


class userDrivingInfo_Score(flask_restful.Resource):
    def __init__(self):
        config = db_config()
        self.db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'], passwd=config['passwd'], db=config['db'], charset='utf8')
        self.cursor = self.db.cursor()
    
    def get(self,user_no):
        query = "SELECT driving_score FROM user WHERE number=%s"
        self.cursor.execute(query, user_no)
        self.db.commit()
        score = self.cursor.fetchone()

        self.db.close()
        response =jsonify({"score": score})
        response.status_code = 200
        return response


api.add_resource(userDrivingInfo_Score, '/users/<int:user_no>/drivingScore')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=env.get('PORT', 5001), debug=True)