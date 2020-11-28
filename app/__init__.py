from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO,send
import logging
from logging.handlers import SMTPHandler


logging.basicConfig(level=logging.DEBUG)
#general configs
app=Flask(__name__)
app.config.from_object(config)
from flask_socketio import SocketIO,send
socketio=SocketIO(app,engineio_logger=True,logger=True)
#DB Configs
db=SQLAlchemy(app)
migrate=Migrate(app,db)
#Login Configs
login=LoginManager(app)
login.login_view='login'
login.message='Please Login To Access The Page'
login.login_message_category='info'


from app import routes,models
