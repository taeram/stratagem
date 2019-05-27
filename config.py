from os import getenv, path

APP_DIR = path.dirname(path.realpath(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    API_KEY = getenv('API_KEY')
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL').replace('mysql2:', 'mysql:')
    MAILGUN_API_URL = "https://api.mailgun.net/v2"
    MAILGUN_API_KEY = getenv('MAILGUN_API_KEY')
    LOCAL_PART_HASH_LENGTH = 8

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
