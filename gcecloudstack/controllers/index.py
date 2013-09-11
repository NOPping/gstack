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
import os


@app.route('/example')
@authentication.required
def example(authorization):
    resp = jsonify({
        "jsessionid": authorization.jsessionid,
        "sessionkey": authorization.sessionkey,
    })
    resp.status_code = 200
    return resp


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


@app.route('/compute/v1beta15/projects/<projectid>')
@authentication.required
def getProject(projectid, authorization):

    command = 'listAccounts'
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
    cloudstack_response = cloudstack_response['listaccountsresponse']['account']
    cloudstack_response = cloudstack_response[0]

    quotas = [{
        'limit': cloudstack_response['vmlimit'],
        'metric': 'vm limit',
        'usage': cloudstack_response['vmtotal'],
    }, {
        'limit': cloudstack_response['iplimit'],
        'metric': 'ip limit',
        'usage': cloudstack_response['iptotal'],
    }, {
        'limit': cloudstack_response['volumelimit'],
        'metric': 'volume limit',
        'usage': cloudstack_response['volumetotal'],
    }, {
        'limit': cloudstack_response['snapshotlimit'],
        'metric': 'snapshot limit',
        'usage': cloudstack_response['snapshottotal'],
    }, {
        'limit': cloudstack_response['templatelimit'],
        'metric': 'template limit',
        'usage': cloudstack_response['templatetotal'],
    }, {
        'limit': cloudstack_response['projectlimit'],
        'metric': 'project limit',
        'usage': cloudstack_response['projecttotal'],
    }, {
        'limit': cloudstack_response['networklimit'],
        'metric': 'network limit',
        'usage': cloudstack_response['networktotal'],
    }, {
        'limit': cloudstack_response['vpclimit'],
        'metric': 'vpc limit',
        'usage': cloudstack_response['vpctotal'],
    }, {
        'limit': cloudstack_response['cpulimit'],
        'metric': 'cpu limit',
        'usage': cloudstack_response['cputotal'],
    }, {
        'limit': cloudstack_response['memorylimit'],
        'metric': 'memory limit',
        'usage': cloudstack_response['memorytotal'],
    }, {
        'limit': cloudstack_response['primarystoragelimit'],
        'metric': 'primary storage limit',
        'usage': cloudstack_response['primarystoragetotal'],
    }, {
        'limit': cloudstack_response['secondarystoragelimit'],
        'metric': 'secondary storage limit',
        'usage': cloudstack_response['secondarystoragetotal'],
    }]

    populated_response = {
        'commonInstanceMetadata': {
            'kind': 'compute#metadata'
        },
        'creationTimestamp': "2013-09-04T17:41:05.702-07:00",
        'kind': 'compute#project',
        'description': cloudstack_response['name'],
        'name': cloudstack_response['name'],
        'id': cloudstack_response['id'],
        'selfLink': '',
        'quotas': quotas
    }

    gcutil_responce = jsonify(populated_response)
    gcutil_responce.status_code = 200
    return gcutil_responce

    return resp


@app.route('/discovery/v1/apis/compute/v1beta15/rest')
def discovery():

    basepath = os.path.dirname(__file__)
    discovery_template = open(
        os.path.join(
            basepath,
            "..",
            "templates/discovery.json"
        ), "r"
    )
    discovery_template = json.loads(discovery_template.read())
    resp = jsonify(discovery_template)

    resp.status_code = 200
    return resp
