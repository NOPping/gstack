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

import urllib
from gstack import app
from flask import jsonify


def create_response(data):
    res = jsonify(data)
    res.status_code = 200

    return res


def get_filter(data):
    filter = {}

    if 'filter' in data:
        filter = urllib.unquote_plus(data['filter'])
        filter = dict(filter.split(' eq ') for values in filter)

    return filter


def filter_by_name(data, name):
    for item in data:
        if item['name'] == name:
            return item
    return None


def get_root_url():
    return 'https://' + \
        app.config['GSTACK_BIND_ADDRESS'] + ':' + app.config['GSTACK_PORT']
