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

from gstack import helpers
from gstack import controllers
from gstack import app, authentication
from gstack.services import requester
from gstack.controllers import errors


def _add_network(authorization, args=None):
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
    args = {'command': 'listSecurityGroups'}
    network_response = controllers.get_item_with_name(authorization, network, args, 'securitygroup')
    if not network_response:
        return None

    securitygroup_id = network_response['id']

    args = {
        'id': securitygroup_id
    }

    return requester.make_request(
        'deleteSecurityGroup',
        args,
        authorization.client_id,
        authorization.client_secret
    )


def _cloudstack_network_to_gce(cloudstack_response):
    response = {}
    response['kind'] = 'compute#network'
    response['id'] = cloudstack_response['id']
    response['name'] = cloudstack_response['name']
    response['description'] = cloudstack_response['description']
    response['selfLink'] = urllib.unquote_plus(request.base_url) + '/' + response['name']

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


def get_network_by_name(authorization, network):
    args = {'command': 'listSecurityGroups'}
    return controllers.get_item_with_name(authorization, network, args, 'securitygroup')


@app.route('/compute/v1/projects/<projectid>/global/networks', methods=['GET'])
@authentication.required
def listnetworks(projectid, authorization):
    args = {'command': 'listSecurityGroups'}
    kwargs = {}
    items = controllers.describe_items(
        authorization, args, 'securitygroup',
        _cloudstack_network_to_gce, **kwargs)

    populated_response = _create_populated_network_response(
        projectid,
        items
    )
    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/global/networks/<network>', methods=['GET'])
@authentication.required
def getnetwork(projectid, authorization, network):
    func_route = url_for('getnetwork', projectid=projectid, network=network)
    args = {'command': 'listSecurityGroups'}
    kwargs = {}
    return controllers.get_item_with_name_or_error(
        authorization, network, args, 'securitygroup', func_route,
        _cloudstack_network_to_gce, **kwargs)


@app.route('/compute/v1/projects/<projectid>/global/networks', methods=['POST'])
@authentication.required
def addnetwork(authorization, projectid):
    data = json.loads(request.data)
    args = {}
    args['name'] = data['name']
    args['description'] = data['description']

    network_result = _add_network(authorization, args)

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
                    'message': 'The resource \'projects/\'' + projectid + '/global/networks/' + args['name']
                }]
            }
        }
    else:
        populated_response = {
            'kind': 'compute#operation',
            'operationType': 'insert',
            'targetLink': urllib.unquote_plus(
                helpers.get_root_url() + url_for(
                    'getnetwork',
                    projectid=projectid,
                    network=data['name']
                )
            ),
            'status': 'DONE',
            'progress': 100
        }

    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/global/networks/<network>', methods=['DELETE'])
@authentication.required
def deletenetwork(projectid, authorization, network):
    response = _delete_network(authorization, projectid, network)

    if not response:
        func_route = url_for(
            'getnetwork',
            projectid=projectid,
            network=network
        )
        return errors.resource_not_found(func_route)

    populated_response = {
        'kind': 'compute#operation',
        'operationType': 'delete',
        'targetLink': '',
        'status': 'DONE',
        'progress': 100
    }

    return helpers.create_response(data=populated_response)
