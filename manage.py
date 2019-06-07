from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager
from config import Config


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
# Integrated flask_script,Initializes a manager object and associated with
# the app
manager = Manager(app)

Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    # It proves that the session has been integrated already
    # redis_store.session = ['name', 'miaomiao']
    return 'success'


if __name__ == '__main__':
    # app.run()
    manager.run()
