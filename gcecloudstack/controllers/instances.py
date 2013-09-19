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


from gcecloudstack import app
from gcecloudstack import authentication
from gcecloudstack.services import requester
from gcecloudstack.controllers import errors, zones, images, machine_type
from flask import jsonify, request, url_for
import json


def _get_instance_from_name(projectid, authorization, zone, instance):
    command = 'listVirtualMachines'
    args = {
        'keyword': instance
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    cloudstack_response = json.loads(cloudstack_response)
    app.logger.debug(
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )
    instance = {}
    if cloudstack_response['listvirtualmachinesresponse']:
        instance = _cloudstack_virtualmachine_to_gce(
            cloudstack_response['listvirtualmachinesresponse'][
                'virtualmachine'][0]
        )
    return instance


def _get_virtualmachine_id(virtualmachine, authorization):
    command = 'listVirtualMachines'
    args = {
        'keyword': virtualmachine
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )
    virtualmachine_id = None
    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        virtualmachine + ' getvirtualid\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    if cloudstack_response['listvirtualmachinesresponse']:
        virtualmachine_id = cloudstack_response[
            'listvirtualmachinesresponse']['virtualmachine'][0]['id']
    return virtualmachine_id


def _cloudstack_virtualmachine_to_gce(response_item):
    def crop_image_length(image):
        if len(image) > 18:
            image = (image[:13]) + '...' + (image[-2:])
        return image

    return ({
        'kind': 'compute#instance',
        'id': response_item['id'],
        'creationTimestamp': response_item['created'],
        'zone': response_item['zonename'],
        'status': response_item['state'],
        'statusMessage': 'VM is ' + response_item['state'],
        'name': response_item['displayname'],
        'description': response_item['displayname'],
        'machineType': response_item['serviceofferingname'],
        'image': crop_image_length(str(response_item['templatename'])),
        'kernel': '',
        'canIpForward': 'true',
        'networkInterfaces': [
            {
                'network': '',
                'networkIP': response_item['nic'][0]['ipaddress'],
                'name': response_item['nic'][0]['id']
            }
            ],

        'selfLink': request.base_url
    })


def _cloudstack_delete_to_gce(cloudstack_response, instance, instanceid):
    return({
        'kind': 'compute#operation',
        'id': 0,
        'creationTimestamp': '',
        'name': '',
        'zone': '',
        'clientOperationId': '',
        'operationType': '',
        'targetLink': '',
        'targetId': 0,
        'status': '',
        'statusMessage': '',
        'user': '',
        'progress': '',
        'insertTime': '',
        'startTime': '',
        'endTime': '',
        'httpErrorStatusCode': 0,
        'httpErrorMessage': '',
        'selfLink': '',
        'region': ''
    })


@app.route('/' + app.config['PATH'] + '<projectid>/aggregated/instances',
           methods=['GET'])
@authentication.required
def aggregatedlistinstances(projectid, authorization):
    command = 'listVirtualMachines'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = json.loads(cloudstack_response)

    instances = []
    if cloudstack_response['listvirtualmachinesresponse']:
        for response_item in cloudstack_response[
                'listvirtualmachinesresponse']['virtualmachine']:
            instances.append(
                _cloudstack_virtualmachine_to_gce(response_item)
            )

    zonelist = zones.get_zone_names(authorization)

    app.logger.debug(
        projectid + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    items = {}
    for zone in zonelist:
        zone_instances = []
        if instances:
            for instance in instances:
                instance['zone'] = zone
                instance['selfLink'] = request.base_url + \
                    '/' + instance['name']
                zone_instances.append(instance)
        else:
            items[zone] = errors.no_results_found(zone)

        items['zone/' + zone] = {}
        items['zone/' + zone]['zone'] = zone
        items['zone/' + zone]['instances'] = zone_instances

    populated_response = {
        'kind': 'compute#instanceAggregatedList',
        'id': 'projects/' + projectid + '/instances',
        'selfLink': request.base_url,
        'items': items
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/instances',
           methods=['GET'])
@authentication.required
def listinstances(projectid, authorization, zone):

    command = 'listVirtualMachines'
    args = {}
    if 'name' in str(request.args):
        print(request.args)
        name = (request.args['filter'].split(' '))[-1]
        instances = [
            _get_instance_from_name(projectid, authorization, zone, name)
        ]
    else:
        cloudstack_response = requester.make_request(
            command,
            args,
            authorization.client_id,
            authorization.client_secret
        )

        cloudstack_response = json.loads(cloudstack_response)
        app.logger.debug(
            projectid + '\n' +
            zone + '\n' +
            json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
        )
        instances = []
        if cloudstack_response['listvirtualmachinesresponse']:
            for response_item in cloudstack_response[
                    'listvirtualmachinesresponse']['virtualmachine']:
                instances.append(
                    _cloudstack_virtualmachine_to_gce(response_item)
                )

    populated_response = {
        'kind': 'compute#instanceList',
        'id': 'projects/' + projectid + '/instances',
        'selfLink': request.base_url,
        'items': instances
    }
    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] +
           '<projectid>/zones/<zone>/instances/<instance>', methods=['GET'])
@authentication.required
def getinstance(projectid, authorization, zone, instance):
    res = jsonify(
        _get_instance_from_name(projectid, authorization, zone, instance)
    )
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] +
           '<projectid>/zones/<zone>/instances/<instance>', methods=['DELETE'])
@authentication.required
def deleteinstance(projectid, authorization, zone, instance):
    command = 'destroyVirtualMachine'
    instanceid = _get_virtualmachine_id(instance, authorization)
    if instanceid is None:
        func_route = url_for('deleteinstance', projectid=projectid,
                             instance=instance, zone=zone)
        return(errors.resource_not_found(func_route))

    args = {
        'id': instanceid
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        projectid + '\n' +
        instance + '\n' +
        zone + '\n' +
        instanceid + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    instance_deleted = _cloudstack_delete_to_gce(
        cloudstack_response,
        instance,
        instanceid
    )

    res = jsonify(instance_deleted)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] +
           '<projectid>/zones/<zone>/instances', methods=['POST'])
@authentication.required
def addinstance(projectid, authorization, zone):

    # TODO: Clean this up
    data = json.loads(request.data)
    print data['machineType'].rsplit('/', 1)[1]
    service_offering_id = data['machineType'].rsplit('/', 1)[1]

    template_id = str(images.get_template_id(
        data['image'].rsplit('/', 1)[1],
        authorization
    ))
    zone_id = str(zones.get_zone_id(zone, authorization))
    instance_name = data['name']

    app.logger.debug(
        projectid + '\n' +
        zone + '\n' +
        instance_name + '\n' +
        service_offering_id + '\n' +
        template_id + '\n' +
        zone_id
    )

    command = 'deployVirtualMachine'
    args = {
        'zoneId': zone_id,
        'templateId': template_id,
        'serviceofferingid': service_offering_id,
        'displayname': instance_name,
        'name': instance_name
    }

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    res = jsonify(operations(
        projectid=projectid,
        operationid=cloudstack_response['deployvirtualmachineresponse']['jobid'],
        authorization=authorization)
    )
    res.status_code = 200

    return res


@app.route('/' + app.config['PATH'] +
           '<projectid>/global/operations/<operationid>', methods=['GET'])
@authentication.required
def getoperations(projectid, operationid, authorization):
    res = jsonify(operations(
        projectid=projectid,
        operationid=operationid,
        authorization=authorization
    ))
    res.status_code = 200

    return res


def operations(projectid, operationid, authorization):
    url_root = 'https://' + app.config['LISTEN_ADDRESS'] + ':' + app.config['LISTEN_PORT']

    command = 'queryAsyncJobResult'
    args = {
        'jobId': operationid
    }

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = json.loads(cloudstack_response)

    cloudstack_response = cloudstack_response['queryasyncjobresultresponse']

    app.logger.debug(
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    if cloudstack_response['jobstatus'] is 1:
        populated_response = {
            'kind': 'compute#operation',
            'id': cloudstack_response['jobid'],
            'name': cloudstack_response['jobid'],
            'zone': url_root + url_for('getzone', projectid=projectid, zone=cloudstack_response['jobresult']['virtualmachine']['zonename']),
            'operationType': 'insert',
            'targetLink': url_root + url_for('getinstance', projectid=projectid, zone=cloudstack_response['jobresult']['virtualmachine']['zonename'], instance=cloudstack_response['jobresult']['virtualmachine']['displayname']),
            'targetId': cloudstack_response['jobresult']['virtualmachine']['id'],
            'status': 'DONE',
            'user': cloudstack_response['userid'],
            'progress': 100,
            'insertTime': cloudstack_response['created'],
            'startTime': cloudstack_response['created'],
            'selfLink': url_root + url_for('getoperations', projectid=projectid, operationid=operationid),
        }
    else:
        populated_response = {
            'kind': 'compute#operation',
            'id': cloudstack_response['jobid'],
            'name': cloudstack_response['jobid'],
            'operationType': 'insert',
            'targetLink': '',
            'status': 'PENDING',
            'user': cloudstack_response['userid'],
            'progress': 0,
            'insertTime': cloudstack_response['created'],
            'startTime': cloudstack_response['created'],
            'selfLink': url_root + url_for('getoperations', projectid=projectid, operationid=operationid),
        }

    return populated_response
