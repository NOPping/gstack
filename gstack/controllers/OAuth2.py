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

import flask
from flask import request
from gstack import app
from gstack.oauth2provider import CloudstackAuthorizationProvider


@app.route('/oauth2/auth', methods=['GET'])
def authorization_code():

    provider = CloudstackAuthorizationProvider()

    response = provider.get_authorization_code_from_uri(request.url)

    res = flask.make_response(response.text, response.status_code)
    for k, v in response.headers.iteritems():
        res.headers[k] = v
    return res


@app.route('/oauth2/token', methods=['POST'])
def token():
    provider = CloudstackAuthorizationProvider()

    data = {k: request.form[k] for k in request.form.iterkeys()}

    response = provider.get_token_from_post_data(data)

    res = flask.make_response(response.text, response.status_code)
    for k, v in response.headers.iteritems():
        res.headers[k] = v
    return res
