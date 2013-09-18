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

import hashlib
import hmac
import base64
import urllib
import requests
from flask import abort
from gcecloudstack import app


def _create_url(url, args, client_id, client_secret):
    args['apiKey'] = client_id
    params = []
    keys = sorted(args.keys())
    for key in keys:
        params.append(key + '=' + urllib.quote_plus(args[key]))
    query = '&'.join(params)
    digest = hmac.new(
        client_secret,
        msg=query.lower(),
        digestmod=hashlib.sha1).digest()
    signature = base64.b64encode(digest)
    query += '&signature=' + urllib.quote_plus(signature)
    return url + '?' + query


def make_request(command, args, client_id, client_secret):
    url = app.config['CLOUDSTACK_PROTOCOL'] + '://' \
        + app.config['CLOUDSTACK_HOST'] + ':' + app.config['CLOUDSTACK_PORT'] \
        + app.config['CLOUDSTACK_PATH']
    args['command'] = command
    args['response'] = 'json'
    url = _create_url(url, args, client_id, client_secret)
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        app.logger.debug(
            'Failed request to cloudstack\n' +
            'status code:' + str(response.status_code) + '\n'
            'text: ' + str(response.text)
        )
        abort(response.status_code)
