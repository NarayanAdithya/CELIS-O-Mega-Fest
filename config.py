import os
basedir=os.path.abspath(os.path.dirname(__file__))

class config(object):
    SECRET_KEY= os.environ.get('SECRET_KEY') or '334nadnj&&89Ydau89YAd98adbszmdi3*&&923kln'
    