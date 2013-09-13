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
from gcecloudstack import authentication
from gcecloudstack.services import requester
from flask import jsonify, request
import json

def _cloudstack_region_to_gcutil(cloudstack_response):
    return ({
        'kind': "compute#region",
        'name': cloudstack_response['name'],
        'description': cloudstack_response['name'],
        'id': cloudstack_response['id'],
        'status': 'UP'
    })


@app.route('/' + app.config['PATH'] + '<projectid>/regions')
@authentication.required
def listregions(projectid, authorization):

    command = 'listRegions'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_responses = json.loads(cloudstack_response)
    cloudstack_responses = cloudstack_responses['listregionsresponse']

    regions = []

    if cloudstack_responses:
        for cloudstack_response in cloudstack_responses['region']:
            regions.append(_cloudstack_region_to_gcutil(cloudstack_response))

    populated_response = {
        'kind': "compute#regionList",
        'id': 'projects/' + projectid + '/regions',
        'selfLink': request.base_url,
        'items': regions
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/regions/<region>')
@authentication.required
def getregion(projectid, authorization, region):
    command = 'listRegions'
    args = {
        'name': region
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)
    if cloudstack_response['listregionsresponse']:
        cloudstack_response = cloudstack_response['listregionsresponse']['region'][0]
        region = _cloudstack_region_to_gcutil(cloudstack_response)
        res = jsonify(region)
        res.status_code = 200
    else:
        res = jsonify({
            'error': {
                'errors': [
                    {
                        "domain": "global",
                        "reason": "notFound",
                        "message": 'The resource \'projects/' + projectid + '/regions/' + region + '\' was not found'
                    }
                ],
                'code': 404,
                'message': 'The resource \'projects/' + projectid + '/regions/' + region + '\' was not found'
            }
        })
        res.status_code = 404
    return res
