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


def _cloudstack_zone_to_gce(response_item):
    translate_zone_status = {
        'Enabled': 'UP',
        'Disabled': 'DOWN'
    }
    return ({
        'kind': "compute#zone",
        'name': response_item['name'],
        'description': response_item['name'],
        'id': response_item['id'],
        'status': response_item['allocationstate']
    })


@app.route('/' + app.config['PATH'] + '<projectid>/zones')
@authentication.required
def listzones(projectid, authorization):
    command = 'listZones'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)
    cloudstack_response = cloudstack_response['listzonesresponse']

    zones = []

    if cloudstack_response:
        for response_item in cloudstack_response['zone']:
            zones.append(_cloudstack_zone_to_gce(response_item))

    populated_response = {
        'kind': "compute#zoneList",
        'id': 'projects/' + projectid + '/zones',
        'selfLink': request.base_url,
        'items': zones
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>')
@authentication.required
def getzone(projectid, authorization, zone):
    command = 'listZones'
    args = {
        'name': zone
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)
    if cloudstack_response['listzonesresponse']:
        response_item = cloudstack_response[
            'listzonesresponse']['zone'][0]
        zone = _cloudstack_zone_to_gce(response_item)
        res = jsonify(zone)
        res.status_code = 200
    else:
        func_route = url_for('getzone', projectid=projectid, zone=zone)
        res = errors.resource_not_found(func_route)

    return res
