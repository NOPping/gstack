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

import json
from flask import request, url_for
from gcecloudstack import app, authentication
from gcecloudstack.services import requester
from gcecloudstack.controllers import zones, helper, operations, images, errors


def _get_instances(authorization, args=None):
    command = 'listVirtualMachines'
    if not args:
        args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def _deploy_virtual_machine(authorization, args):
    command = 'deployVirtualMachine'

    converted_args = {}
    converted_args['templateid'] = images.get_template_id(
        args['template'], authorization
    )
    converted_args['zoneid'] = zones.get_zone_id(
        args['zone'], authorization
    )
    converted_args['serviceofferingid'] = args['serviceoffering']
    converted_args['displayname'] = args['name']
    converted_args['name'] = args['name']

    cloudstack_response = requester.make_request(
        command,
        converted_args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def _cloudstack_instance_to_gce(cloudstack_response, selfLink=None, zone=None):
    response = {}
    response['kind'] = 'compute#instance'
    response['id'] = cloudstack_response['id']
    response['creationTimestamp'] = cloudstack_response['created']
    response['status'] = cloudstack_response['state'].upper()
    response['name'] = cloudstack_response['name']
    response['description'] = cloudstack_response['name']
    response['machineType'] = cloudstack_response['serviceofferingname']
    response['image'] = cloudstack_response['templatename']
    response['canIpForward'] = 'true'
    response['networkInterfaces'] = []

    networking = {}
    networking['network'] = 'tobereviewed'
    networking['networkIP'] = cloudstack_response['nic'][0]['ipaddress']
    networking['name'] = cloudstack_response['nic'][0]['id']

    response['networkInterfaces'].append(networking)

    if not selfLink:
        response['selfLink'] = request.base_url
    else:
        response['selfLink'] = selfLink

    if not zone:
        response['zone'] = cloudstack_response['zonename']
    else:
        response['zone'] = zone

    return response


@app.route('/' + app.config['PATH'] + '<projectid>/aggregated/instances', methods=['GET'])
@authentication.required
def aggregatedlistinstances(authorization, projectid):
    zone_list = zones.get_zone_names(authorization)
    instances_list = _get_instances(authorization)

    items = {}

    for zone in zone_list:
        zones_instances = []
        if instances_list['listvirtualmachinesresponse']:
            for instance in instances_list['listvirtualmachinesresponse']['virtualmachine']:
                zones_instances.append(
                    _cloudstack_instance_to_gce(
                        cloudstack_response=instance,
                        zone=zone,
                        selfLink=request.base_url + '/' + instance['name']
                    )
                )
        items['zone/' + zone] = {}
        items['zone/' + zone]['zone'] = zone
        items['zone/' + zone]['instances'] = zones_instances

    populated_response = {
        'kind': 'compute#instanceAggregatedList',
        'id': 'projects/' + projectid + '/instances',
        'selfLink': request.base_url,
        'items': items
    }

    return helper.create_response(data=populated_response)


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/instances', methods=['GET'])
@authentication.required
def listinstances(authorization, projectid, zone):
    instance = None
    filter = helper.get_filter(request.args)

    if 'name' in filter:
        instance = filter['name']

    items = []

    if instance:
        instance_list = _get_instances(
            authorization,
            args={'keyword': instance}
        )
        if instance_list['listvirtualmachinesresponse']:
            instance = helper.filter_by_name(
                data=instance_list['listvirtualmachinesresponse']['virtualmachine'],
                name=instance
            )
            if instance:
                items.append(_cloudstack_instance_to_gce(instance))
    else:
        instance_list = _get_instances(authorization)
        if instance_list['listvirtualmachinesresponse']:
            for instance in instance_list['listvirtualmachinesresponse']['virtualmachine']:
                items.append(_cloudstack_instance_to_gce(instance))

    populated_response = {
        'kind': 'compute#instance_list',
        'id': 'projects/' + projectid + '/instances',
        'selfLink': request.base_url,
        'items': items
    }

    return helper.create_response(data=populated_response)


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/instances/<instance>', methods=['GET'])
@authentication.required
def getinstance(projectid, authorization, zone, instance):
    instance_list = _get_instances(
        authorization,
        args={'keyword': instance}
    )

    if instance_list['listvirtualmachinesresponse']:
        response = helper.filter_by_name(
            data=instance_list['listvirtualmachinesresponse']['virtualmachine'],
            name=instance
        )
        return helper.create_response(
            data=_cloudstack_instance_to_gce(response)
        )
    else:
        func_route = url_for('getinstance', projectid=projectid, zone=zone, instance=instance)
        return errors.resource_not_found(func_route)


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/instances', methods=['POST'])
@authentication.required
def addinstance(authorization, projectid, zone):
    data = json.loads(request.data)
    args = {}
    args['name'] = data['name']
    args['serviceoffering'] = data['machineType'].rsplit('/', 1)[1]
    args['template'] = data['image'].rsplit('/', 1)[1]
    args['zone'] = zone

    deploymentResult = _deploy_virtual_machine(authorization, args)

    if 'errortext' in deploymentResult['deployvirtualmachineresponse']:
        populated_response = {
            'kind': 'compute#operation',
            'operationType': 'insert',
            'targetLink': '',
            'status': 'DONE',
            'progress': 100,
            'error': {
                'errors': [{
                    'code': 'RESOURCE_ALREADY_EXISTS',
                    'message': 'the resource \'projects/\'' + projectid + '/zones/' + zone + '/instances/' +
                    args['name']
                }]
            }
        }
    else:
        populated_response = operations.create_response(
            projectid=projectid,
            operationid=deploymentResult['deployvirtualmachineresponse']['jobid'],
            authorization=authorization
        )

    return helper.create_response(data=populated_response)
