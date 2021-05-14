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


app = Flask(__name__, static_url_path='/public', static_folder='./public')

# Controllers API

@app.route('/')
def index():
    return 

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
    app.run(host='0.0.0.0', port=env.get('PORT', 3000), debug=True)
    #app.run(debug=True)
