from app import app
from flask import request,redirect,url_for,render_template,flash,get_flashed_messages


@app.route('/')
@app.route('/index')
def index():
    return render_template('celis.html')
