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
import argparse

from flask import Flask
from ConfigParser import SafeConfigParser

from gstack.core import db


def _generate_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-p',
        '--profile',
        required=False,
        help='The profile to run gstack with, default is initial',
        default='initial'
    )

    parser.add_argument(
        '-d',
        '--debug',
        required=False,
        help='Turn debug on for application',
        default=False
    )

    args = parser.parse_args()

    return vars(args)


def _load_config_file():
    config_file = os.path.join(
        os.path.expanduser('~'),
        '.gstack/gstack.conf'
    )
    if not os.path.exists(config_file):
        sys.exit('No configuration found, please run gstack-configure')

    return config_file


def _load_database():
    database_file = os.path.join(
        os.path.expanduser('~'),
        '.gstack/gstack.sqlite'
    )

    if not os.path.exists(database_file):
        sys.exit('No database found, please run gstack-configure')

    return 'sqlite:///' + database_file


def _config_from_config_profile(config_file, profile):
    config = SafeConfigParser()
    config.read(config_file)

    if not config.has_section(profile):
        sys.exit('No profile matching ' + profile
                 + ' found in configuration, please run gstack-configure -p '
                 + profile)

    for attribute in config.options(profile):
        app.config[attribute.upper()] = config.get(profile, attribute)


def configure_app(settings=None):
    app.config['DATA'] = os.path.abspath(os.path.dirname(__file__)) + '/data'
    app.config['PATH'] = 'compute/v1/projects/'

    db.init_app(app)

    if settings:
        app.config.from_object(settings)
    else:
        args = _generate_args()
        profile = args.pop('profile')
        app.config['DEBUG'] = args.pop('debug')
        config_file = _load_config_file()
        database_uri = _load_database()
        _config_from_config_profile(config_file, profile)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri


app = Flask(__name__)

publickey_storage = {}

from gstack.controllers import *

basedir = os.path.abspath(os.path.dirname(__file__))
