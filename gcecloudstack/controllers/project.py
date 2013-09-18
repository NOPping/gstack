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
from flask import jsonify, request, url_for
import json


def _format_quota(limit, metric, usage):
    return ({
        'limit': limit,
        'metric': metric,
        'usage': usage,
    })


def _cloudstack_quotas_to_gce(quotas):

    names = {'vm', 'ip', 'volume', 'snapshot', 'template', 'project',
             'network'
             }
    gce_quotas = []
    for name in names:
        gce_quotas.append(
            _format_quota(quotas[name + 'limit'], name, quotas[name + 'total'])
        )
    return gce_quotas


@app.route('/' + app.config['PATH'] + '<projectid>', methods=['GET'])
@authentication.required
def getproject(projectid, authorization):
    command = 'listAccounts'
    args = {
        'name': projectid
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        'Processing request for listzones\n'
        'Project: ' + projectid + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    if cloudstack_response['listaccountsresponse']:
        response_item = cloudstack_response[
            'listaccountsresponse']['account'][0]

        quotas = _cloudstack_quotas_to_gce(response_item)

        populated_response = {
            'commonInstanceMetadata': {
                'kind': 'compute#metadata'
            },
            'creationTimestamp': '2013-09-04T17:41:05.702-07:00',
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
        func_route = url_for('getproject', projectid=projectid)
        res = errors.resource_not_found(func_route)

    return res


@app.route('/' + app.config['PATH'] + '<projectid>/setCommonInstanceMetadata',
           methods=['POST'])
@authentication.required
def setglobalmetadata(projectid, authorization):

    res = jsonify({
        "kind": "compute#operation",
        "id": '',
        'name': '',
        'operationType': 'setMetadata',
        'targetLink': '',
        'targetId': '',
        'status': '',
        'user': projectid,
        'progress': 0,
        'insertTime': '',
        'startTime': '',
        'selfLink': request.base_url
    })
    res.status_code = 200
    return res
