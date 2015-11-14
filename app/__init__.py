import os
from flask import Flask

app = Flask(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

import logging
from logging import FileHandler
file_handler = FileHandler(filename="%s/stratagem.log" % app.config['LOG_DIR'])
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)

import filters
import views
