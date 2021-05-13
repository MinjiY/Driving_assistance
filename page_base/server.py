from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

import constants


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


@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response




# Controllers API
@app.route('/dashboard')
def dashboard():
    return render_template('main.html')


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
    app.run(host='0.0.0.0', port=env.get('PORT', 3000))
