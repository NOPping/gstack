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
from gcecloudstack.controllers import errors
from flask import jsonify, request, url_for
import json


def _cloudstack_region_to_gce(response_item):
    return ({
        'kind': 'compute#region',
        'name': response_item['name'],
        'description': response_item['name'],
        'id': response_item['id'],
        'status': 'UP'
    })


@app.route('/' + app.config['PATH'] + '<projectid>/regions', methods=['GET'])
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

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        'Processing request for listregions\n'
        'Project: ' + projectid + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    cloudstack_response = cloudstack_response['listregionsresponse']

    regions = []

    if cloudstack_response:
        for response_item in cloudstack_response['region']:
            regions.append(_cloudstack_region_to_gce(response_item))

    populated_response = {
        'kind': 'compute#regionList',
        'id': 'projects/' + projectid + '/regions',
        'selfLink': request.base_url,
        'items': regions
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/regions/<region>',
           methods=['GET'])
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

    app.logger.debug(
        'Processing request for getregion\n'
        'Project: ' + projectid + '\n' +
        'Region: ' + region + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    if cloudstack_response['listregionsresponse']:
        response_item = cloudstack_response[
            'listregionsresponse']['region'][0]
        region = _cloudstack_region_to_gce(response_item)
        res = jsonify(region)
        res.status_code = 200
    else:
        func_route = url_for('getregion', projectid=projectid, region=region)
        res = errors.resource_not_found(func_route)

    return res
