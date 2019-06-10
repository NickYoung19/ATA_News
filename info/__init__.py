from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler


# Initialize a sqlalchemy instance object db to be associated with the app
db = SQLAlchemy()


def set_log(config_name):
    """Implement the project log function"""
    # Set the record level of the log
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    # Create a logger and specify the path to save the log
    file_log_handler = RotatingFileHandler(
        "logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # Create a logging format
    formatter = logging.Formatter(
        '%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # Set format
    file_log_handler.setFormatter(formatter)
    # Using global logging
    logging.getLogger().addHandler(file_log_handler)


redis_store = None


def create_app(config_name):
    """
    By passing in different configuration name,
    initialize the application instances of their corresponding configurations
    """
    set_log(config_name)
    app = Flask(__name__)

    # Integrated configuration class
    app.config.from_object(config[config_name])

    # Integrated salalchemy and associated with the app
    # db = SQLAlchemy(app)
    db.init_app(app)

    # Integrated redis,Integrate keyword parameter into config classes and
    # quote
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[
                              config_name].REDIS_PORT)

    # CRSFProtect relate to the object app, Set csrf_token to form and cookie
    CSRFProtect(app)

    # Integrated flask_session app
    Session(app)

    # Registered index blueprint
    # ps: When to use when to import, can solve the loop import issue
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    # Registered passport blueprint
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    # The factory function returns the created program instance
    return app
