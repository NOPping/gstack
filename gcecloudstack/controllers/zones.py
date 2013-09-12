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
from flask import jsonify
import json


@app.route('/' + app.config['PATH'] + '<projectid>/zones')
@authentication.required
def listzones(projectid, authorization):

    command = 'listZones'
    args = {}
    logger = None
    cloudstack_response = requester.make_request(
        command,
        args,
        logger,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)
    cloudstack_response = cloudstack_response['listzonesresponse']

    zones = []

    # test for empty response, i.e no zones available
    if cloudstack_response:
        for zone in cloudstack_response['zone']:
            zones.append({
                'kind': "compute#zone",
                'name': zone['name'],
                'description': zone['name'],
                'id': zone['id'],
                'status': zone['allocationstate']
            })

    populated_response = {
        'kind': "compute#zoneList",
        'id': '',
        'selfLink': '',
        'items': zones
    }

    gcutil_response = jsonify(populated_response)
    gcutil_response.status_code = 200
    return gcutil_response
