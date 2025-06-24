# config.py is a configuration file that contains the configuration settings for the Flask application.
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_APP_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

