from flask import Flask
from application.config import DevelopmentConfig
from application.config import ProductionConfig
import os

app = Flask(__name__)
if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'production':
	app.config.from_object(ProductionConfig)
else:
	app.config.from_object(DevelopmentConfig)

import routes