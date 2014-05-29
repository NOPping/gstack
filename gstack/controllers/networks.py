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

import urllib
import json
from flask import request, url_for
from gstack import app, authentication
from gstack.services import requester
from gstack.controllers import helper, errors


def _get_networks(authorization, args=None):
    command = 'listSecurityGroups'
    if not args:
        args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def get_network_by_name(authorization, securitygroup):
    securitygroup_list = _get_networks(
        authorization=authorization,
        args={
            'keyword': securitygroup
        }
    )

    if securitygroup_list['listsecuritygroupsresponse']:
        response = helper.filter_by_name(
            data=securitygroup_list[
                'listsecuritygroupsresponse']['securitygroup'],
            name=securitygroup
        )
        return response
    else:
        return None


def _get_network(authorization, args=None):
    command = 'createSecurityGroup'
    if not args:
        args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def _delete_network(authorization, projectid, network):
    securitygroup_id = get_network_by_name(authorization, network)['id']

    if securitygroup_id is None:
        func_route = url_for(
            'getnetwork',
            projectid=projectid,
            network=network
        )

        return errors.resource_not_found(func_route)

    args = {
        'id': securitygroup_id
    }

    return requester.make_request(
        'deleteSecurityGroup',
        args,
        authorization.client_id,
        authorization.client_secret
    )


def _cloudstack_network_to_gce(cloudstack_response, selfLink=None):
    response = {}
    response['kind'] = 'compute#network'
    response['id'] = cloudstack_response['id']
    response['name'] = cloudstack_response['name']
    response['description'] = cloudstack_response['description']

    if selfLink:
        response['selfLink'] = urllib.unquote_plus(selfLink)
    else:
        response['selfLink'] = urllib.unquote_plus(request.base_url)

    return response


def _create_populated_network_response(projectid, networks=None):
    if not networks:
        networks = []
    populated_response = {
        'kind': 'compute#networkList',
        'selfLink': request.base_url,
        'id': 'projects/' + projectid + '/global/networks',
        'items': networks
    }
    return populated_response


@app.route(
    '/compute/v1/projects/<projectid>/global/networks', methods=['GET'])
@authentication.required
def listnetworks(projectid, authorization):
    securitygroup_list = _get_networks(
        authorization=authorization
    )

    networks = []
    if securitygroup_list['listsecuritygroupsresponse']:
        for network in securitygroup_list['listsecuritygroupsresponse']['securitygroup']:
            networks.append(_cloudstack_network_to_gce(
                cloudstack_response=network,
                selfLink=request.base_url + '/' + network['name']))

    populated_response = _create_populated_network_response(
        projectid,
        networks
    )
    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/global/networks/<network>', methods=['GET'])
@authentication.required
def getnetwork(projectid, authorization, network):
    response = get_network_by_name(
        authorization=authorization,
        securitygroup=network
    )

    if response:
        return helper.create_response(
            data=_cloudstack_network_to_gce(response)
        )
    else:
        func_route = url_for(
            'getnetwork',
            projectid=projectid,
            network=network)
        return errors.resource_not_found(func_route)


@app.route('/compute/v1/projects/<projectid>/global/networks', methods=['POST'])
@authentication.required
def addnetwork(authorization, projectid):
    data = json.loads(request.data)
    args = {}
    args['name'] = data['name']
    args['description'] = data['description']

    network_result = _get_network(authorization, args)

    if 'errortext' in network_result['createsecuritygroupresponse']:
        populated_response = {
            'kind': 'compute#operation',
            'operationType': 'insert',
            'targetLink': '',
            'status': 'DONE',
            'progress': 100,
            'error': {
                'errors': [{
                    'code': 'RESOURCE_ALREADY_EXISTS',
                    'message': 'the resource \'projects/\'' + projectid + '/global/networks/' + args['name']
                }]
            }
        }
    else:
        populated_response = {
            'kind': 'compute#operation',
            'operationType': 'insert',
            'targetLink': urllib.unquote_plus(
                helper.get_root_url() + url_for(
                    'getnetwork',
                    projectid=projectid,
                    network=data['name']
                )
            ),
            'status': 'DONE',
            'progress': 100
        }

    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/global/networks/<network>', methods=['DELETE'])
@authentication.required
def deletenetwork(projectid, authorization, network):
    _delete_network(authorization, projectid, network)

    populated_response = {
        'kind': 'compute#operation',
        'operationType': 'delete',
        'targetLink': '',
        'status': 'DONE',
        'progress': 100
    }

    return helper.create_response(data=populated_response)
