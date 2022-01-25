from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
import logging
from logging.handlers import SMTPHandler
from flask_mail import Mail

logging.basicConfig(level=logging.DEBUG)


## general configs
app=Flask(__name__)
app.config.from_object(config)
from flask_socketio import SocketIO,send
socketio=SocketIO(app,engineio_logger=True,logger=True)


## DB Configs
db=SQLAlchemy(app)
migrate=Migrate(app,db)


## Login Configs
login=LoginManager(app)
login.login_view='auth.loginUser'
login.message='Please Login To Access The Page'
login.login_message_category='info'

## MAIL SETTINGS
mail = Mail(app)
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='CELIS INTERNAL SERVER ISSUES',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

## Blueprint Registrations
from app.auth import auth
from app.course import course
from app.recommender import recommender
from app.forum import forum
from app.home import home

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(course, url_prefix='/course')
app.register_blueprint(recommender, url_prefix='/recommender')
app.register_blueprint(forum, url_prefix='/forum')
app.register_blueprint(home, url_prefix = '')

from .utils import errorhandlers