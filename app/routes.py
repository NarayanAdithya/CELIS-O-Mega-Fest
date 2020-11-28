from app import app,socketio
from flask import request,redirect,url_for,render_template,flash,get_flashed_messages


@app.route('/')
@app.route('/index')
def index():
    return render_template('celis.html',title='Home',data_footer_aos="fade-left",data_aos_footer_delay=100,data_aos_header="fade-left",data_header_aos_delay=100)


@app.route('/course')
def course():
    return 0

@app.route('/forum')
def forum():
    return 0