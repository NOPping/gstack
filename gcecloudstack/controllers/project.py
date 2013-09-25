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
from gcecloudstack.controllers import errors, helper
from flask import jsonify, request, url_for
import json
import urllib


def _format_quota(limit, metric, usage):
    return ({
        'limit': limit,
        'metric': metric,
        'usage': usage,
    })


def _list_ssh_keys(authorization):
    command = 'listTags'
    args = {
        'resourcetype': 'UserVm',
        'key': 'sshkey'
    }

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    sshkeys = []
    if cloudstack_response['listtagsresponse']:
        for tag in cloudstack_response['listtagsresponse']['tag']:
            sshkeys.append(tag['value'])

    print str(set(sshkeys))

    return sshkeys


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

    _list_ssh_keys(authorization)

    if cloudstack_response['listaccountsresponse']:
        response_item = cloudstack_response[
            'listaccountsresponse']['account'][0]

        quotas = _cloudstack_quotas_to_gce(response_item)

        populated_response = {
            'commonInstanceMetadata': {
                'kind': 'compute#metadata'
            },
            'creationTimestamp': response_item['user'][0]['created'],
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
        func_route = urllib.unquote_plus(url_for('getproject', projectid=projectid))
        res = errors.resource_not_found(func_route)

    return res


@app.route('/' + app.config['PATH'] + '<projectid>/setCommonInstanceMetadata', methods=['POST'])
@authentication.required
def setglobalmetadata(projectid, authorization):
    data = json.loads(request.data)
    data = data['items'][0]['value'].split(':')[1]

    command = 'registerSSHKeyPair'
    args = {
        'name': projectid,
        'publickey': data
    }

    requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret,
    )

    res = jsonify({
        "kind": "compute#operation",
        'operationType': 'setMetadata',
        'targetLink': urllib.unquote_plus(helper.get_root_url() + url_for(
            'getproject',
            projectid=projectid
        )),
        'status': 'PENDING',
        'progress': 0
    })
    res.status_code = 200
    return res
