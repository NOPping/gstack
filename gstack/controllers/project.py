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
# under the License.from gcloud import app

from gstack import app, publickey_storage
from gstack import authentication
from gstack.services import requester
from gstack.controllers import errors, helper
from flask import jsonify, request, url_for
import json
import urllib
import collections


def _list_ssh_keys(authorization):
    command = 'listTags'
    args = {
        'resourcetype': 'UserVm',
        'keyword': 'sshkey-segment'
    }

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    resources = {}
    sshkeys = set()

    if cloudstack_response['listtagsresponse']:
        for tag in cloudstack_response['listtagsresponse']['tag']:
            if tag['resourceid'] not in resources:
                resources[tag['resourceid']] = {}
            resources[tag['resourceid']][tag['key']] = tag['value']
        for resource in resources:
            sorted_resource = collections.OrderedDict(
                sorted(
                    resources[resource].items()))
            sshkey = ''
            for keychunk in sorted_resource:
                sshkey = sshkey + sorted_resource[keychunk]
            sshkeys.add(sshkey)

    sshkeys = '\n'.join(sshkeys)

    return sshkeys


def _get_accounts(authorization, args=None):
    command = 'listAccounts'
    if not args:
        args = {}

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def _get_account_by_name(authorization, projectid):
    account_list = _get_accounts(
        authorization=authorization,
        args={
            'keyword': projectid
        }
    )

    if account_list['listaccountsresponse']:
        response = helper.filter_by_name(
            data=account_list['listaccountsresponse']['account'],
            name=projectid
        )
        return response
    else:
        return None


def _format_quota(metric, limit, usage):
    quota = {}
    quota['metric'] = metric
    quota['limit'] = limit
    quota['usage'] = usage
    return quota


def _populate_quotas(cloudstack_response):
    quotas = []

    quota_names = {}
    quota_names['INSTANCE'] = 'vm'
    quota_names['DISKS'] = 'volume'
    quota_names['SNAPSHOTS'] = 'snapshot'
    quota_names['IMAGES'] = 'template'

    for name in quota_names:
        quotas.append(
            _format_quota(
                name,
                cloudstack_response[quota_names[name] + 'limit'],
                cloudstack_response[quota_names[name] + 'total']
            )
        )

    return quotas


def _cloudstack_project_to_gce(cloudstack_response, metadata=None):
    if not metadata:
        metadata = {}

    quotas = _populate_quotas(cloudstack_response)

    response = {}
    response['kind'] = 'compute#project'
    response['id'] = cloudstack_response['id']
    response['creationTimestamp'] = cloudstack_response['user'][0]['created']
    response['name'] = cloudstack_response['name']
    response['description'] = cloudstack_response['name']
    response['selfLink'] = request.base_url

    if metadata:
        response['commonInstanceMetadata'] = {}
        response['commonInstanceMetadata']['kind'] = 'compute#metadata'
        response['commonInstanceMetadata']['items'] = []

    if quotas:
        response['quotas'] = quotas

    if 'sshKeys' in metadata and metadata['sshKeys']:
        sshKeys = {}
        sshKeys['key'] = 'sshKeys'
        sshKeys['value'] = metadata['sshKeys']
        response['commonInstanceMetadata']['items'].append(sshKeys)

    return response


@app.route('//compute/v1/projects/<projectid>', methods=['GET'])
@authentication.required
def getproject(authorization, projectid):
    project = _get_account_by_name(authorization, projectid)

    if project:
        metadata = {}
        metadata['sshKeys'] = _list_ssh_keys(authorization)
        publickey_storage[projectid] = metadata['sshKeys']

        res = jsonify(_cloudstack_project_to_gce(project, metadata))
        res.status_code = 200
    else:
        func_route = urllib.unquote_plus(
            url_for(
                'getproject',
                projectid=projectid))
        res = errors.resource_not_found(func_route)

    return res


@app.route('//compute/v1/projects/<projectid>/setCommonInstanceMetadata', methods=['POST'])
@authentication.required
def setglobalmetadata(projectid, authorization):
    data = json.loads(request.data)
    publickey_storage[projectid] = data['items'][0]['value']
    data = data['items'][0]['value'].split(':')[1]

    command = 'deleteSSHKeyPair'
    args = {
        'name': projectid
    }

    requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret,
    )

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
