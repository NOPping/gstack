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

import sys
import os
import json

from gcecloudstack import app
from flask import jsonify

from gcecloudstack.services import requester
from gcecloudstack import authentication


class machine_type_resource(object):
    def __init__(self):
        self.kind = "compute#machineType"
        self.id = ''
        self.creationTimestamp = ''
        self.name = ''
        self.description = ''
        self.guestCpus = ''
        self.memoryMb = ''
        self.imageSpaceGb = ''
        self.scratchDisks = [
                             {
                              "diskGb": ''
                             }
                            ]
        self.maximumPersistentDisks = ''
        self.maximumPersistentDisksSizeGb = ''
        self.deprecated = {
                           "state": '',
                           "replacement": '',
                           "deprecated": '',
                           "obsolete": '',
                           "deleted": ''
                           }
        self.zone = ''
        self.selfLink = ''

class typeencoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__

@app.route('/compute/v1beta15/projects/<project>/aggregated/machineTypes')
@authentication.required
def aggregatedlist(authorization, project):
    command = 'listServiceOfferings'
    args = {}
    logger = None
    response = requester.make_request(command, args, logger, authorization.jsessionid, authorization.sessionkey)
    print response
    response = json.loads(response)
    response = response['listserviceofferingsresponse']['serviceoffering']
    result = []
    for res in response:
        tmp = machine_type_resource()
        tmp.name = res['name']
        tmp.description = res['displaytext']
        result.append(typeencoder(tmp))
    return json.dumps(tuple(result))
    
@app.route('/compute/v1beta15/projects/<project>/zones/<zone>/machineTypes/<machinetype>')
@authentication.required
def getmachinetype(authorization, project, zone, machinetype):
    command = 'listServiceOfferings'
    args = {'keyword': machinetype}
    logger = None
    response = requester.make_request(command, args, logger, authorization.jsessionid, authorization.sessionkey)
    response = json.loads(response)
    response = response['listserviceofferingsresponse']['serviceoffering'][0]

    tmp = machine_type_resource()
    tmp.name = response['name']
    tmp.id = response['id']
    tmp.guestCpus = response['cpunumber']
    tmp.description = response['displaytext']
    tmp.creationTimestamp = response['created']
    tmp.memoryMb = response['memory']
    
    return json.dumps(tmp, cls=typeencoder)
    
@app.route('/compute/v1beta15/projects/<project>/zones/<zone>/machineTypes')
@authentication.required
def listmachinetype(authorization, project, zone):    
    command = 'listServiceOfferings'
    args = None
    logger = None
    response = requester.make_request(command, args, logger, authorization.jsessionid, authorization.sessionkey)
    print response
    response = json.loads(response)
    response = response['listserviceofferingsresponse']['serviceoffering']
    resp = jsonify(response)
    resp.status_code = 200
    return resp

# this is just an example to show how to use different http verbs
'''
@app.route('/user/<uuid>', methods=['GET', 'DELETE', 'PATCH'])
def user(uuid):
    if request.method == 'GET':
        response, error = requester.make_request('listUsers', {'id': uuid}, None, app.config['HOST'], app.config[
                                                 'PORT'], app.config['API_KEY'], app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
        return response
    elif request.method == 'PATCH':
        data = request.json
        data['id'] = uuid
        response, error = requester.make_request(
            'updateUser', data, None, app.config['HOST'],
            app.config['PORT'], app.config['API_KEY'], app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
        return response
    else:
        response, error = requester.make_request(
            'deleteUser', {'id': uuid}, None, app.config['HOST'],
            app.config['PORT'], app.config['API_KEY'], app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
        return response

@app.route('/user', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        return requester.make_request(
            'listUsers', None, None, app.config[
                'HOST'], app.config['PORT'], app.config['API_KEY'],
            app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
    else:
        Need to pass a json dictionary in the request to feed to the POST update !!!
        response, error = requester.make_request(
            'createUser', request.json, None, app.config['HOST'],
            app.config['PORT'], app.config['API_KEY'], app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
        return response
'''
