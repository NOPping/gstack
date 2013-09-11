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
# under the License.from gcecloudstack import app

from gcecloudstack import app
from gcecloudstack import authentication
from gcecloudstack.services import requester
from flask import jsonify
import json

@app.route('/' + app.config['PATH']  + '<projectid>')
@authentication.required
def getProject(projectid, authorization):

    command = 'listAccounts'
    args = {
        'name': projectid
    }
    logger = None
    cloudstack_response = requester.make_request(
        command,
        args,
        logger,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)
    cloudstack_response = cloudstack_response['listaccountsresponse']['account'][0]

    quotas = [{
        'limit': cloudstack_response['vmlimit'],
        'metric': 'Virtual Machine',
        'usage': cloudstack_response['vmtotal'],
    }, {
        'limit': cloudstack_response['iplimit'],
        'metric': 'IP',
        'usage': cloudstack_response['iptotal'],
    }, {
        'limit': cloudstack_response['volumelimit'],
        'metric': 'Volume',
        'usage': cloudstack_response['volumetotal'],
    }, {
        'limit': cloudstack_response['snapshotlimit'],
        'metric': 'Snapshot',
        'usage': cloudstack_response['snapshottotal'],
    }, {
        'limit': cloudstack_response['templatelimit'],
        'metric': 'Template',
        'usage': cloudstack_response['templatetotal'],
    }, {
        'limit': cloudstack_response['projectlimit'],
        'metric': 'Project',
        'usage': cloudstack_response['projecttotal'],
    }, {
        'limit': cloudstack_response['networklimit'],
        'metric': 'Network',
        'usage': cloudstack_response['networktotal'],
    }, {
        'limit': cloudstack_response['vpclimit'],
        'metric': 'VPC',
        'usage': cloudstack_response['vpctotal'],
    }, {
        'limit': cloudstack_response['cpulimit'],
        'metric': 'CPU',
        'usage': cloudstack_response['cputotal'],
    }, {
        'limit': cloudstack_response['memorylimit'],
        'metric': 'Memory',
        'usage': cloudstack_response['memorytotal'],
    }, {
        'limit': cloudstack_response['primarystoragelimit'],
        'metric': 'Primary storage',
        'usage': cloudstack_response['primarystoragetotal'],
    }, {
        'limit': cloudstack_response['secondarystoragelimit'],
        'metric': 'Secondary storage',
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
