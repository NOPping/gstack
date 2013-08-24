from flask import Flask
import os

app = Flask(__name__)
app.config['CLOUDSTACK_URL'] = "http://localhost:8080"

from application.controllers import *