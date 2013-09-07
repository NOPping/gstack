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
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import requests
from gcecloudstack import app
import urllib


def make_request(command, args, logger, jsessionid, sessionkey):
    url = app.config['PROTOCOL'] + "://" + app.config[
        'HOST'] + ":" + app.config['PORT'] + app.config['PATH']
    cookies = dict(jsessionid=jsessionid,
                   sessionkey=urllib.quote_plus(sessionkey))
    payload = {'command': command, 'response':
               'json', 'sessionkey': sessionkey}
    response = requests.get(url, cookies=cookies, params=payload)

    return response.text


def cloud_login(username, password):
    url = app.config['PROTOCOL'] + "://" + app.config[
        'HOST'] + ":" + app.config['PORT'] + app.config['PATH']
    payload = {'command': 'login', 'username':
               username, 'password': password, 'response': 'json'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}
    request = requests.post(url=url, params=payload, headers=headers)

    if request.status_code == 200:
        return request
    else:
        return None
