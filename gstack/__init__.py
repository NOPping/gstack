#!/usr/bin/env python
# encoding: utf-8
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os
import sys

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


def _load_config_file():
    config_file = os.path.join(
        os.path.expanduser('~'),
        '.gstack/gstack.conf'
    )

    if not os.path.exists(config_file):
        sys.exit('No configuration found, please run gstack-configure')

    return config_file


def configure_app():
    config_file = _load_config_file()
    app.config.from_pyfile(config_file)
    app.config['DATA'] = os.path.abspath(os.path.dirname(__file__)) + '/data'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(app.config['DATA'], 'app.db')


app = Flask(__name__)

db = SQLAlchemy(app)
publickey_storage = {}

from gstack.controllers import *


basedir = os.path.abspath(os.path.dirname(__file__))

db.create_all()
