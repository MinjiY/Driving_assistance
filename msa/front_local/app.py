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

########################## 시연때 꼭 수정해야하는 파라미터
temp_userNumber = "1"
##########################


import consul

client = consul.Consul(host='172.19.0.100', port=8500)
serviceName="users"
service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
service_port = client.catalog.service(serviceName)[1][0]['ServicePort']
users_url = "http://{}:{}".format(service_address, service_port)

print(serviceName)
print(service_address)
print(service_port)

serviceName="totalcal_driving"
service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
service_port = client.catalog.service(serviceName)[1][0]['ServicePort']
totalcal_driving_url = "http://{}:{}".format(service_address, service_port)

print(serviceName)
print(service_address)
print(service_port)

serviceName="driving_date"
service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
service_port = client.catalog.service(serviceName)[1][0]['ServicePort']
driving_date_url = "http://{}:{}".format(service_address, service_port)

print(serviceName)
print(service_address)
print(service_port)

serviceName="driving_score"
service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
service_port = client.catalog.service(serviceName)[1][0]['ServicePort']
driving_score_url = "http://{}:{}".format(service_address, service_port)

print(serviceName)
print(service_address)
print(service_port)


# DB
config = db_config()
db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'],
                     passwd=config['passwd'], db=config['db'], charset='utf8')
cursor = db.cursor()


## login

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


@app.route('/health', methods=['GET'])
def health():
    return 'This is health check page'

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
        cursor.execute(query, (userinfo['sub'], userinfo['name'], userinfo['picture']))
        db.commit()
        db.close()
    except:
        pass
    try:
        query = """select Number from user where name=%s"""
        cursor.execute(query, (userinfo['name']))
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


@app.route('/profile')
def profile():

    
    response = requests.get(users_url+'/users/'+temp_userNumber)
    content_data=response.json()

    return render_template('profile.html', userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4), user_info=content_data)

@app.route('/main')
def main():

    response = requests.get(totalcal_driving_url+'/users/'+temp_userNumber+'/driving')
    json_data=response.json()


    return render_template('main.html', userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4), content_data=json_data)



@app.route('/drivingInfo')
def drivingInfo():

    response = requests.get(driving_date_url+'/users/'+temp_userNumber+'/driving/dates')
    json_data=response.json()
    
    return render_template('drivingInfo.html', userinfo=session[constants.PROFILE_KEY], userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4),content_data=json_data)


@app.route('/drivingInfo_detail/<string:drivingDate>/<string:start>')
def drivingInfo_detail(drivingDate,start):

    response = requests.get(driving_date_url+'/users/'+temp_userNumber+'/driving/dates/'+drivingDate+ '/'+ start)
    json_data=response.json()

    return render_template('drivingInfo_detail.html',userinfo=session[constants.PROFILE_KEY],userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4),driving_date=json_data["driving_date"],start_time=json_data["start_time"], End_time=json_data["End_time"], videoSrc=json_data["videoSrc"],count_data=json_data["count_data"], total_time=json_data["total_time"],driving_info=json_data["driving_info"])



@app.route('/drivingScore')
def drivingScore():

    userinfo = session[constants.PROFILE_KEY]

    response = requests.get(totalcal_driving_url+'/users/'+temp_userNumber+'/driving')
    content_data=response.json()


    response = requests.get(driving_score_url+"/users/"+temp_userNumber+"/drivingScore")
    #print(response)
    score=response.json()

    return render_template('drivingScore.html', userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4), score=score["score"], content_data=content_data)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404



### admin
@app.route('/admin/users')
def users():

    response = requests.get(users_url+'/users')
    content_data=response.json()

    return render_template('userListView.html', userinfo=session[constants.PROFILE_KEY], userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4), datas=content_data)


@app.route('/admin/users/<int:number>')
def userDetail(number):

    response = requests.get(totalcal_driving_url+'/users/'+temp_userNumber+'/driving')
    json_data=response.json()


    ## 사용자 이름만 가져옴 => 서비스로 x
    config = db_config()
    db = pymysql.connect(host=config['host'], port=config['port'], user=config['user'],
                     passwd=config['passwd'], db=config['db'], charset='utf8')
    cursor = db.cursor()
    sql = 'select name from user where number=%s'
    cursor.execute(sql,number)
    db.commit()
    user_name_query = cursor.fetchone()
    db.close()
    user_name=user_name_query[0]

    return render_template('userDetailView.html', userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4), content_data=json_data, user_name=user_name)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env.get('PORT', 3000), debug=True)
    # app.run(debug=True)
