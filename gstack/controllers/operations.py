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
from gstack import app, publickey_storage
from gstack import authentication
from gstack.controllers import helper
from gstack.services import requester
from flask import url_for


def _get_async_result(authorization, args):
    command = 'queryAsyncJobResult'
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    return cloudstack_response


def _delete_instance_response(async_result, projectid):
    populated_response = {
        'kind': 'compute#operation',
        'insertTime': async_result['created'],
        'operationType': 'delete',
        'name': async_result['jobid'],
        'startTime': async_result['created'],
        'selfLink': urllib.unquote_plus(helper.get_root_url() + url_for(
            'getoperations',
            projectid=projectid,
            operationid=async_result['jobid']
        ))
    }

    if async_result['jobstatus'] is 0:
        # handle pending case
        populated_response['targetLink'] = ''
        populated_response['status'] = 'PENDING'
        populated_response['progress'] = 0
    elif async_result['jobstatus'] is 1:
        # handle successful case
        populated_response['status'] = 'DONE'
        populated_response['zone'] = urllib.unquote_plus(
            helper.get_root_url() +
            url_for(
                'getzone',
                projectid=projectid,
                zone=async_result['jobresult']['virtualmachine']['zonename'],
            ))
        populated_response['targetLink'] = urllib.unquote_plus(
            helper.get_root_url() +
            url_for(
                'getinstance',
                projectid=projectid,
                zone=async_result['jobresult']['virtualmachine']['zonename'],
                instance=async_result['jobresult']['virtualmachine']['displayname']))

    # need to add a case here for error handling, its job status 2

    return populated_response


def _add_sshkey_metadata(authorization, publickey, instanceid):
    l = publickey
    n = 100
    split_publickey = [l[i:i + n] for i in range(0, len(l), n)]
    i = 0
    for datasegment in split_publickey:
        print datasegment
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


def _create_instance_response(async_result, projectid, authorization):
    populated_response = {
        'kind': 'compute#operation',
        'id': async_result['jobid'],
        'operationType': 'insert',
        'name': async_result['jobid'],
        'user': async_result['userid'],
        'insertTime': async_result['created'],
        'startTime': async_result['created'],
        'selfLink': urllib.unquote_plus(helper.get_root_url() + url_for(
            'getoperations',
            projectid=projectid,
            operationid=async_result['jobid']
        ))
    }

    if async_result['jobstatus'] is 0:
        # handle pending case
        populated_response['targetLink'] = ''
        populated_response['status'] = 'PENDING'
        populated_response['progress'] = 0
    elif async_result['jobstatus'] is 1:
        # handle successful case
        populated_response['status'] = 'DONE'
        populated_response['id'] = async_result['jobid']
        populated_response['zone'] = urllib.unquote_plus(
            helper.get_root_url() +
            url_for(
                'getzone',
                projectid=projectid,
                zone=async_result['jobresult']['virtualmachine']['zonename'],
            ))
        populated_response['targetLink'] = urllib.unquote_plus(
            helper.get_root_url() +
            url_for(
                'getinstance',
                projectid=projectid,
                zone=async_result['jobresult']['virtualmachine']['zonename'],
                instance=async_result['jobresult']['virtualmachine']['displayname']))
        _add_sshkey_metadata(
            authorization=authorization,
            publickey=publickey_storage[projectid],
            instanceid=async_result['jobresult']['virtualmachine']['id']
        )

    return populated_response


def create_response(authorization, projectid, operationid):
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
    return helper.create_response(create_response(
        authorization=authorization,
        operationid=operationid,
        projectid=projectid
    ))
