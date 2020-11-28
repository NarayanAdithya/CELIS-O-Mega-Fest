from app import app

if __name__ == '__main__':
    socketio.run(app,log_output=True,)
