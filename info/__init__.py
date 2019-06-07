from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session


app = Flask(__name__)

# Integrated configuration class
app.config.from_object(Config)

# Integrated salalchemy and associated with the app
db = SQLAlchemy(app)

# Integrated redis,Integrate keyword parameter into config classes and quote
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# CRSFProtect relate to the object app, Set csrf_token to form and cookie
CSRFProtect(app)

# Integrated flask_session app
Session(app)
