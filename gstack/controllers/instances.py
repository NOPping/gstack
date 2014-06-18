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
import urllib
from gstack import helpers
from gstack import controllers
from flask import request, url_for
from gstack import app, authentication
from gstack.services import requester
from gstack.controllers import zones, operations, images, errors, machine_type, networks


def _deploy_virtual_machine(authorization, args, projectid):
    command = 'deployVirtualMachine'

    converted_args = {}
    template = images.get_template_by_name(
        authorization=authorization,
        image=args['template']
    )
    converted_args['templateid'] = template['id']

    zone = zones.get_zone_by_name(
        authorization=authorization,
        zone=args['zone']
    )
    converted_args['zoneid'] = zone['id']

    serviceoffering = machine_type.get_machinetype_by_name(
        authorization=authorization,
        machinetype=args['serviceoffering']
    )
    converted_args['serviceofferingid'] = serviceoffering['id']

    if 'network' in args:
        network = networks.get_network_by_name(
            authorization=authorization,
            securitygroup=args['network']
        )
        converted_args['securitygroupids'] = network['id']

    converted_args['displayname'] = args['name']
    converted_args['name'] = args['name']
    converted_args['keypair'] = projectid

    cloudstack_response = requester.make_request(
        command,
        converted_args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def _destroy_virtual_machine(authorization, instance):
    virtual_machine_id = _get_virtual_machine_by_name(
        authorization,
        instance)['id']

    if virtual_machine_id is None:
        func_route = url_for('_destroy_virtual_machine', instance=instance)
        return errors.resource_not_found(func_route)

    args = {
        'id': virtual_machine_id
    }
    return requester.make_request(
        'destroyVirtualMachine',
        args,
        authorization.client_id,
        authorization.client_secret
    )


def _cloudstack_virtual_machine_to_gce(cloudstack_response, projectid, zone, **kwargs):
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
    response['disks'] = []

    networking = {}
    accessconfig = []
    accessconfig.append({})
    if 'securitygroup' in cloudstack_response:
        networking['network'] = cloudstack_response['securitygroup'][0]['name']
        networking['networkIP'] = cloudstack_response['nic'][0]['ipaddress']
        networking['name'] = cloudstack_response['nic'][0]['id']
        accessconfig[0]['natIP'] = cloudstack_response['nic'][0]['ipaddress']
        networking['accessConfigs'] = []

    accessconfig[0]['kind'] = 'compute#accessConfig'
    accessconfig[0]['type'] = 'ONE_TO_ONE_NAT'
    accessconfig[0]['name'] = 'External NAT'

    networking['accessConfigs'] = accessconfig

    response['networkInterfaces'].append(networking)

    response['selfLink'] = urllib.unquote_plus(helpers.get_root_url() + url_for(
        'getinstance',
        projectid=projectid,
        instance=cloudstack_response['name'],
        zone=zone
    ))
    response['zone'] = zone

    return response


@app.route('/compute/v1/projects/<projectid>/aggregated/instances', methods=['GET'])
@authentication.required
def aggregatedlistinstances(authorization, projectid):
    args = {'command':'listVirtualMachines'}
    kwargs = {'projectid':projectid}
    items = controllers.describe_items_aggregated(
        authorization, args, 'virtualmachine', 'instances',
        _cloudstack_virtual_machine_to_gce, **kwargs)

    populated_response = {
        'kind': 'compute#instanceAggregatedList',
        'id': 'projects/' + projectid + '/instances',
        'selfLink': request.base_url,
        'items': items
    }
    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/instances', methods=['GET'])
@authentication.required
def listinstances(authorization, projectid, zone):
    args = {'command':'listVirtualMachines'}
    kwargs = {'projectid':projectid, 'zone':zone}
    items = controllers.describe_items(
        authorization, args, 'virtualmachine',
        _cloudstack_virtual_machine_to_gce, **kwargs)

    populated_response = {
        'kind': 'compute#instance_list',
        'id': 'projects/' + projectid + '/instances',
        'selfLink': request.base_url,
        'items': items
    }

    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/instances/<instance>', methods=['GET'])
@authentication.required
def getinstance(projectid, authorization, zone, instance):
    func_route = url_for('getinstance', projectid=projectid, zone=zone, instance=instance)
    args = {'command':'listVirtualMachines'}
    return controllers.get_item_with_name_or_error(authorization, zone, args, 'zone',
                                errors.resource_not_found(func_route))


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/instances', methods=['POST'])
@authentication.required
def addinstance(authorization, projectid, zone):
    data = json.loads(request.data)
    args = {}
    args['name'] = data['name']
    args['serviceoffering'] = data['machineType'].rsplit('/', 1)[1]
    args['template'] = data['disks'][0]['initializeParams']['sourceImage'].rsplit('/', 1)[1]
    args['zone'] = zone

    network = data['networkInterfaces'][0]['network'].rsplit('/', 1)[1]
    if network is not 'default':
        args['network'] = network

    deployment_result = _deploy_virtual_machine(authorization, args, projectid)

    if 'errortext' in deployment_result['deployvirtualmachineresponse']:
        populated_response = {
            'kind': 'compute#operation',
            'operationType': 'insert',
            'targetLink': '',
            'status': 'DONE',
            'progress': 100,
            'error': {
                'errors': [{
                    'code': 'RESOURCE_ALREADY_EXISTS',
                    'message': 'the resource \'projects/\'' + projectid +
                               '/zones/' + zone + '/instances/' + args['name']
                }]
            }
        }
    else:
        populated_response = operations.create_response(
            projectid=projectid,
            operationid=deployment_result['deployvirtualmachineresponse']['jobid'],
            authorization=authorization
        )

    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/instances/<instance>', methods=['DELETE'])
@authentication.required
def deleteinstance(projectid, authorization, zone, instance):
    deletion_result = _destroy_virtual_machine(authorization, instance)

    populated_response = operations.create_response(
        projectid=projectid,
        operationid=deletion_result['destroyvirtualmachineresponse']['jobid'],
        authorization=authorization
    )

    return helpers.create_response(data=populated_response)