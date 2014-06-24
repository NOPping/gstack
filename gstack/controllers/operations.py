#!/usr/bin/env python
# encoding: utf-8
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

import urllib

from flask import url_for

from gstack import app, publickey_storage
from gstack import authentication
from gstack import helpers
from gstack.services import requester


def _get_async_result(authorization, args):
    command = 'queryAsyncJobResult'
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    return cloudstack_response


def _get_instance_async_response(async_result, projectid, type):
    response = {}
    response['kind'] = 'compute#operation'
    response['id'] = async_result['jobid']
    response['operationType'] = type
    response['name'] = async_result['jobid']
    response['insertTime'] = async_result['created']
    response['startTime'] = async_result['created']
    response['selfLink'] = urllib.unquote_plus(
        helpers.get_root_url() + url_for(
            'getoperations',
            projectid=projectid,
            operationid=async_result['jobid']
        ))

    if async_result['jobstatus'] is 0:
        response['targetLink'] = ''
        response['status'] = 'PENDING'
        response['progress'] = 0
    elif async_result['jobstatus'] is 1:
        response['status'] = 'DONE'
        response['zone'] = urllib.unquote_plus(
            helpers.get_root_url() +
            url_for(
                'getzone',
                projectid=projectid,
                zone=async_result['jobresult']['virtualmachine']['zonename'],
            ))
        response['targetLink'] = urllib.unquote_plus(
            helpers.get_root_url() +
            url_for(
                'getinstance',
                projectid=projectid,
                zone=async_result['jobresult']['virtualmachine']['zonename'],
                instance=async_result['jobresult']['virtualmachine']['name']))

    return response


def _delete_instance_response(async_result, projectid):
    populated_response = _get_instance_async_response(async_result, projectid, 'delete')
    return populated_response


def _create_instance_response(async_result, projectid, authorization):
    populated_response = _get_instance_async_response(async_result, projectid, 'insert')
    populated_response['user'] = async_result['userid']

    if async_result['jobstatus'] is 1:
        _add_sshkey_metadata(
            authorization=authorization,
            publickey=publickey_storage[projectid],
            instanceid=async_result['jobresult']['virtualmachine']['id']
        )

    return populated_response


def _add_sshkey_metadata(authorization, publickey, instanceid):
    l = publickey
    n = 100
    split_publickey = [l[i:i + n] for i in range(0, len(l), n)]
    i = 0
    for datasegment in split_publickey:
        _add_sshkey_metadata_segment(
            authorization, str(i) + '-sshkey-segment', datasegment, instanceid)
        i = i + 1


def _add_sshkey_metadata_segment(authorization, keyname, value, instanceid):
    command = 'createTags'
    args = {
        'tags[0].key': keyname,
        'tags[0].value': value,
        'resourceids': instanceid,
        'resourcetype': 'UserVm'
    }

    requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )


def create_async_response(authorization, projectid, operationid):
    async_result = _get_async_result(
        authorization=authorization,
        args={'jobId': operationid}
    )

    command_name = None
    populated_response = {}

    if async_result['queryasyncjobresultresponse']:
        async_result = async_result['queryasyncjobresultresponse']
        command_name = async_result['cmd'].rsplit('.', 1)[1]

    if command_name == 'DeployVMCmd':
        populated_response = _create_instance_response(
            async_result=async_result,
            projectid=projectid,
            authorization=authorization
        )
    elif command_name == 'DestroyVMCmd':
        populated_response = _delete_instance_response(
            async_result=async_result,
            projectid=projectid
        )

    return populated_response


@app.route('/compute/v1/projects/<projectid>/global/operations/<operationid>', methods=['GET'])
@authentication.required
def getoperations(authorization, operationid, projectid):
    return helpers.create_response(create_async_response(
        authorization=authorization,
        operationid=operationid,
        projectid=projectid
    ))
