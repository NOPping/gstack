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
from gcecloudstack.controllers import errors
from flask import jsonify, request
import json


def _cloudstack_quotas_to_gce(response_item):
    return ([{
        'limit': response_item['vmlimit'],
        'metric': 'Virtual Machine',
        'usage': response_item['vmtotal'],
    }, {
        'limit': response_item['iplimit'],
        'metric': 'IP',
        'usage': response_item['iptotal'],
    }, {
        'limit': response_item['volumelimit'],
        'metric': 'Volume',
        'usage': response_item['volumetotal'],
    }, {
        'limit': response_item['snapshotlimit'],
        'metric': 'Snapshot',
        'usage': response_item['snapshottotal'],
    }, {
        'limit': response_item['templatelimit'],
        'metric': 'Template',
        'usage': response_item['templatetotal'],
    }, {
        'limit': response_item['projectlimit'],
        'metric': 'Project',
        'usage': response_item['projecttotal'],
    }, {
        'limit': response_item['networklimit'],
        'metric': 'Network',
        'usage': response_item['networktotal'],
    }, {
        'limit': response_item['vpclimit'],
        'metric': 'VPC',
        'usage': response_item['vpctotal'],
    }, {
        'limit': response_item['cpulimit'],
        'metric': 'CPU',
        'usage': response_item['cputotal'],
    }, {
        'limit': response_item['memorylimit'],
        'metric': 'Memory',
        'usage': response_item['memorytotal'],
    }, {
        'limit': response_item['primarystoragelimit'],
        'metric': 'Primary storage',
        'usage': response_item['primarystoragetotal'],
    }, {
        'limit': response_item['secondarystoragelimit'],
        'metric': 'Secondary storage',
        'usage': response_item['secondarystoragetotal'],
    }])


@app.route('/' + app.config['PATH'] + '<projectid>')
@authentication.required
def getproject(projectid, authorization):
    command = 'listAccounts'
    args = {
        'name': projectid
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )
    cloudstack_response = json.loads(cloudstack_response)

    if cloudstack_response['listaccountsresponse']:
        response_item = cloudstack_response[
            'listaccountsresponse']['account'][0]

        quotas = _cloudstack_quotas_to_gce(response_item)

        populated_response = {
            'commonInstanceMetadata': {
                'kind': 'compute#metadata'
            },
            'creationTimestamp': "2013-09-04T17:41:05.702-07:00",
            'kind': 'compute#project',
            'description': response_item['name'],
            'name': response_item['name'],
            'id': response_item['id'],
            'selfLink': request.base_url,
            'quotas': quotas
        }

        res = jsonify(populated_response)
        res.status_code = 200
    else:
        message = 'The resource \'projects/' + projectid + '\' was not found'
        res = errors.resource_not_found(message)

    return res
