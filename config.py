import logging
from redis import StrictRedis


class Config(object):
    SECRET_KEY = '123456789'
    SQLALCHEMY_DATABASE_URI = "mysql://root:nicklogin@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Define two class properties to support dynamic modification
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # Specifies session stored mode
    SESSION_TYPE = 'redis'
    # Specifies session stored object
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # Set session signature and make it confidential
    SESSION_USER_SINGER = True
    # Cancel permanent save
    SESSION_PERMANT = False
    # Set session's lifetime
    PERMANENT_SESSION_LIFETIME = 86400 * 2


class DevelopConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductConfig(Config):
    """ProductConfig environment configuration"""
    DEBUG = False
    LOG_LEVEL = logging.WARNING


class TestingConfig(object):
    """ProductConfig environment configuration"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


config = {
    'develop': DevelopConfig,
    'product': ProductConfig,
    'testing': TestingConfig
}
