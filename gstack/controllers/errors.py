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
from flask import jsonify, Response


@app.errorhandler(404)
def not_found(e):
    return Response('Not Found', status=404, mimetype='text/html')


@app.errorhandler(401)
def unauthorized(e):
    res = jsonify({
        'error': {
            'errors': [
                {
                    'domain': 'global',
                    'reason': 'required',
                    'message': 'Login Required',
                    'locationType': 'header',
                    'location': 'Authorization',
                },
            ],
        },
        'code': 401,
        'message': 'Login Required',
    })

    res.status_code = 401
    return res


def resource_not_found(func_url):
    res = jsonify({
        'error': {
            'errors': [
                {
                    'domain': 'global',
                    'reason': 'notFound',
                    'message': 'The resource \'' + urllib.unquote_plus(func_url) + '\' was not found'
                }
            ],
            'code': 404,
            'message': 'The resource \'' + urllib.unquote_plus(func_url) + '\' was not found'
        }
    })
    res.status_code = 404
    return res


def no_results_found(scope):
    return ({
        "warning": {
            "code": "NO_RESULTS_ON_PAGE",
            "message": "There are no results for scope" + scope + " on this page.",
            "data": [{
                "key": "scope",
                "value": scope
            }]
        }
    })
