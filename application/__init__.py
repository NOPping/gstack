from flask import Flask
import os

app = Flask(__name__)

# Configuration Options

app.config['API_KEY'] = 'apikey'
app.config['SECRET_KEY'] = 'secretkey'
app.config['PATH'] = '/client/api'
app.config['HOST'] = 'localhost'
app.config['PORT'] = '8080'
app.config['PROTOCOL'] = 'http'

from application.controllers import *