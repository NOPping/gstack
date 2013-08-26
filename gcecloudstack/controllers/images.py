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

from gcecloudstack import app
from flask import jsonify, Response

"""
Method	HTTP request	                                  Description
delete	DELETE  /project/global/images/image	          Deletes the specified image resource.
deprecate POST  /project/global/images/image/deprecate	  Sets the deprecation status of an image. If no message body is given, clears the deprecation status instead.
get	GET  /project/global/images/image	          Returns the specified image resource.
insert	POST  /project/global/images	                  Creates an image resource in the specified project using the data included in the request.
list	GET  /project/global/images	                  Retrieves the list of image resources available to the specified project.
"""


@app.route('/project/global/images', methods=['GET', 'POST'])
def user(uuid):
    if request.method == 'GET':
        response, error = requester.make_request(
            'listTemplates', {'id': uuid}, None, app.config['HOST'],
            app.config['PORT'], app.config['API_KEY'], app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
        return response
    elif request.method == 'PATCH':
        data = request.json
        data['id'] = uuid
        response, error = requester.make_request(
            'listTemplates', data, None, app.config['HOST'],
            app.config['PORT'], app.config['API_KEY'], app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
        return response

# show how to use post with json dict


@app.route('/project/global/images/<image>', methods=['GET', 'DELETE'])
def users():
    if request.method == 'GET':
        return requester.make_request(
            'listTemplates', None, None, app.config[
                'HOST'], app.config['PORT'], app.config['API_KEY'],
            app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
    elif request.method == 'DELETE':
        '''Need to pass a json dictionary in the request to feed to the update !!!'''
        response, error = requester.make_request('listTemplates', request.json, None, app.config['HOST'], app.config[
                                                 'PORT'], app.config['API_KEY'], app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
        return response
