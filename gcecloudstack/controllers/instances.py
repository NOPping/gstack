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

from . import helper
from flask import request
from gcecloudstack import app
from gcecloudstack import authentication
from gcecloudstack.services import requester
from gcecloudstack.controllers import zones
import json
import urllib


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
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def _cloudstack_instance_to_gce(response_item, selfLink=None, zone=None):
    cloudstack = {}
    cloudstack['kind'] = 'compute#instance'
    cloudstack['id'] = response_item['id']
    cloudstack['creationTimestamp'] = response_item['created']
    cloudstack['status'] = response_item['state'].upper()
    cloudstack['name'] = response_item['displayname']
    cloudstack['description'] = response_item['displayname']
    cloudstack['machineType'] = response_item['serviceofferingname']
    cloudstack['image'] = response_item['templatename']
    cloudstack['canIpForward'] = 'true'
    cloudstack['networkInterfaces'] = []

    networking = {}
    networking['network'] = 'tobereviewed'
    networking['networkIP'] = response_item['nic'][0]['ipaddress']
    networking['name'] = response_item['nic'][0]['id']

    cloudstack['networkInterfaces'].append(networking)

    if not selfLink:
        cloudstack['selfLink'] = request.base_url
    else:
        cloudstack['selfLink'] = selfLink

    if not zone:
        cloudstack['zone'] = response_item['zonename']
    else:
        cloudstack['zone'] = zone

    return cloudstack


@app.route('/' + app.config['PATH'] + '<projectid>/aggregated/instances', methods=['GET'])
@authentication.required
def aggregatedlistinstances(authorization, projectid):
    zonelist = zones.get_zone_names(authorization)
    instancesList = _get_instances(authorization)

    items = {}

    for zone in zonelist:
        zones_instances = []
        if instancesList['listvirtualmachinesresponse']:
            for instance in instancesList['listvirtualmachinesresponse']['virtualmachine']:
                zones_instances.append(
                    _cloudstack_instance_to_gce(
                        response_item=instance,
                        zone=zone,
                        selfLink=request.base_url +
                        '/' + instance['displayname']
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

    return helper.createsuccessfulresponse(data=populated_response)


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/instances', methods=['GET'])
@authentication.required
def listinstances(authorization, projectid, zone):
    instance = None

    if 'filter' in request.args:
        filter = urllib.unquote_plus(request.args['filter'])
        filter = dict(filter.split(' eq ') for values in filter)
        if filter['name']:
            instance = filter['name']

    if instance:
        cloudstack_response = _get_instances(
            authorization, args={'keyword': instance})
    else:
        cloudstack_response = _get_instances(authorization)

    items = []
    if cloudstack_response['listvirtualmachinesresponse']:
        for instance in cloudstack_response['listvirtualmachinesresponse']['virtualmachine']:
            items.append(_cloudstack_instance_to_gce(instance))

    populated_response = {
        'kind': 'compute#instanceList',
        'id': 'projects/' + projectid + '/instances',
        'selfLink': request.base_url,
        'items': items
    }

    return helper.createsuccessfulresponse(data=populated_response)


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/instances/<instance>', methods=['GET'])
@authentication.required
def getinstance(projectid, authorization, zone, instance):
    cloudstack_response = _get_instances(
        authorization,
        args={'keyword': instance}
    )

    return helper.createsuccessfulresponse(
        data=_cloudstack_instance_to_gce(cloudstack_response['listvirtualmachinesresponse']['virtualmachine'][0])
    )


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/instances/<instance>', methods=['POST'])
@authentication.requred
def addinstance(authorization, projectid, zone):
    data = json.loads(request.data)
    args = {}
    args['name'] = data['name']
    args['serviceoffering'] = data['machineType'].rsplit('/', 1)[1]
    args['template'] = data['image'].rsplit('/', 1)[1]
    args['zone'] = zone

    deploymentResult = _deploy_virtual_machine(authorization, args)

    populated_response = operations.create_response(
        projectid=projectid,
        operationid=deploymentResult['deployvirtualmachineresponse']['jobid'],
        authorization=authorization
    )

    return helper.createsuccessfulresponse(data=populated_response)
