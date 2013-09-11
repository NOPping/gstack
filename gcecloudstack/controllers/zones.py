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

@app.route('/compute/v1beta15/projects/<projectid>/zones')
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
    cloudstack_response = cloudstack_response['listzonesresponse']['zone']

    zones = []

    for item in cloudstack_response:
        zones.append({
            'kind': "compute#zone",
            'name': item['name'],
            'description': item['name'],
            'id': item['id'],
            'status': item['allocationstate']
        })

    populated_response = {
        'kind': "compute#zoneList",
        'id': '',
        'selfLink': '',
        'items': zones
    }

    gcutil_responce = jsonify(populated_response)
    gcutil_responce.status_code = 200
    return gcutil_responce
