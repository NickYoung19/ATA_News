from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session

# Initialize a sqlalchemy instance object db to be associated with the app
db = SQLAlchemy()


def create_app(config_name):
    """
    By passing in different configuration name,
    initialize the application instances of their corresponding configurations
    """
    app = Flask(__name__)

    # Integrated configuration class
    app.config.from_object(config[config_name])

    # Integrated salalchemy and associated with the app
    # db = SQLAlchemy(app)
    db.init_app(app)

    # Integrated redis,Integrate keyword parameter into config classes and
    # quote
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[
                              config_name].REDIS_PORT)

    # CRSFProtect relate to the object app, Set csrf_token to form and cookie
    CSRFProtect(app)

    # Integrated flask_session app
    Session(app)
    # The factory function returns the created program instance
    return app
