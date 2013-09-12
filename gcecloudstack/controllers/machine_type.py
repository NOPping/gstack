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
from flask import jsonify, Response, request, url_for

from gcecloudstack.services import requester
from gcecloudstack.controllers import zones
from gcecloudstack import authentication


@app.route('/' + app.config['PATH'] + '<project>/aggregated/machineTypes')
@authentication.required
def aggregatedlist(authorization, project):
    command = 'listServiceOfferings'
    args = {}
    logger = None
    response = requester.make_request(command, args, logger,
                                      authorization.jsessionid,
                                      authorization.sessionkey)
    print response
    response = json.loads(response)
    response = response['listserviceofferingsresponse']['serviceoffering']

    result = []
    for res in response:
        tmp = {
            'name': res['name'],
            'description': res['displaytext'],
            'id': res['id'],
            'creationTimestamp': res['created'],
            'guestCpus': res['cpunumber'],
            'memoryMb': res['memory']
        }
        result.append(tmp)

    #tmp = {'machineTypes':result}
    res = {
        'kind': "compute#machineTypeAggregatedList",
        'id': 'blah',
        'selfLink': '',
        'items': {
            'Dummy Zone': {'machineTypes': result},
            'Another Zone': {'machineTypes': result}
        }
    }

    for v in res['items'].values():
        print v.get('machineTypes')

    return json.dumps(res)


@app.route('/' + app.config['PATH'] +
           '<project>/zones/<zone>/machineTypes/<machinetype>')
@authentication.required
def getmachinetype(authorization, project, zone, machinetype):
    command = 'listServiceOfferings'
    args = {'keyword': machinetype}
    logger = None
    response = requester.make_request(command, args, logger,
                                      authorization.jsessionid,
                                      authorization.sessionkey)
    response = json.loads(response)
    response = response['listserviceofferingsresponse']['serviceoffering'][0]

    res = {
        'name': response['name'],
        'description': response['displaytext'],
        'id': response['id'],
        'creationTimestamp': response['created'],
        'guestCpus': response['cpunumber'],
        'memoryMb': response['memory']
    }

    return json.dumps(res)


@app.route('/' + app.config['PATH'] + '<project>/zones/<zone>/machineTypes')
@authentication.required
def listmachinetype(authorization, project, zone):
    command = 'listServiceOfferings'
    args = {}
    logger = None
    response = requester.make_request(command, args, logger,
                                      authorization.jsessionid,
                                      authorization.sessionkey)
    print response
    response = json.loads(response)
    response = response['listserviceofferingsresponse']['serviceoffering']

    result = []
    for res in response:
        tmp = {
            'name': res['name'],
            'description': res['displaytext'],
            'id': res['id'],
            'creationTimestamp': res['created'],
            'guestCpus': res['cpunumber'],
            'memoryMb': res['memory']
        }
        result.append(tmp)

    res = {
        'kind': "compute#machineTypeList",
        'id': 'blah',
        'selfLink': '',
        'items': result
    }

    return json.dumps(res)
