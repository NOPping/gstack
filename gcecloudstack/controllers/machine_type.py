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

from gcecloudstack import app
from gcecloudstack import authentication
from gcecloudstack.services import requester
from gcecloudstack.controllers import errors, zones
from flask import jsonify, request, url_for
import json


def _cloudstack_machinetype_to_gce(response_item):
    return ({
        "kind": "compute#machineType",
        'name': response_item['name'],
        'description': response_item['displaytext'],
        'id': response_item['id'],
        'creationTimestamp': response_item['created'],
        'guestCpus': response_item['cpunumber'],
        'memoryMb': response_item['memory']
    })


@app.route('/' + app.config['PATH'] + '<projectid>/aggregated/machineTypes',
           methods=['GET'])
@authentication.required
def aggregatedlistmachinetypes(projectid, authorization):
    command = 'listServiceOfferings'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        'Processing request for aggregated list machine type\n'
        'Project: ' + projectid + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    machine_types = []
    if cloudstack_response['listserviceofferingsresponse']:
        for response_item in cloudstack_response[
                'listserviceofferingsresponse']['serviceoffering']:
            machine_types.append(
                _cloudstack_machinetype_to_gce(response_item))

    zonelist = zones.get_zone_names(authorization)

    items = {}
    for zone in zonelist:
        zone_machine_types = []
        if machine_types:
            for machineType in machine_types:
                machineType['zone'] = zone
                machineType['selfLink'] = request.base_url + \
                    '/' + machineType['name']
                zone_machine_types.append(machineType)
        else:
            zone_machine_types.append(errors.no_results_found(zone))

        items['zone/' + zone] = {}
        items['zone/' + zone]['zone'] = zone
        items['zone/' + zone]['machineTypes'] = zone_machine_types

    populated_response = {
        'kind': 'compute#machineTypeAggregatedList',
        'id': 'projects/' + projectid + '/aggregated/machineTypes',
        'selfLink': request.base_url,
        'items': items
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] +
           '<projectid>/zones/<zone>/machineTypes/<machinetype>',
           methods=['GET'])
@authentication.required
def getmachinetype(projectid, authorization, zone, machinetype):
    command = 'listServiceOfferings'
    args = {
        'keyword': machinetype
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )
    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        'Processing request for get machine type\n'
        'Project: ' + projectid + '\n' +
        'Zone: ' + zone + '\n' +
        'Machine Type:' + machinetype + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    if cloudstack_response['listserviceofferingsresponse']:
        response_item = cloudstack_response[
            'listserviceofferingsresponse']['serviceoffering'][0]
        machine_type = _cloudstack_machinetype_to_gce(response_item)
        res = jsonify(machine_type)
        res.status_code = 200

    else:
        func_route = url_for('getmachinetype', projectid=projectid,
                             machinetype=machinetype, zone=zone)
        res = errors.resource_not_found(func_route)

    return res


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/machineTypes',
           methods=['GET'])
@authentication.required
def listmachinetype(projectid, authorization, zone):
    command = 'listServiceOfferings'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        'Processing request for list machine type\n'
        'Project: ' + projectid + '\n' +
        'Zone: ' + zone + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    machine_types = []
    if cloudstack_response['listserviceofferingsresponse']:
        for response_item in cloudstack_response[
                'listserviceofferingsresponse']['serviceoffering']:
            machine_types.append(
                _cloudstack_machinetype_to_gce(response_item))

        zone_machine_types = []
        for machineType in machine_types:
            machineType['zone'] = zone
            machineType['selfLink'] = request.base_url + \
                '/' + machineType['name']
            zone_machine_types.append(machineType)

    populated_response = {
        'kind': 'compute#machineTypeList',
        'id': 'projects/' + projectid + '/zones/' + zone + '/machineTypes',
        'selfLink': request.base_url,
        'items': zone_machine_types
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res
