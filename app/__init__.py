from flask import Flask
from config import config
from flask_socketio import SocketIO


app=Flask(__name__)
app.config.from_object(config)

socketio=SocketIO(app,engineio_logger=True,logger=True)


from app import routes