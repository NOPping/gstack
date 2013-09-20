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
from gcecloudstack.controllers import errors, zones, helper
from flask import request, url_for


def _get_machinetypes(authorization, args=None):
    command = 'listServiceOfferings'
    if not args:
        args = {}

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    return cloudstack_response


def get_machinetype_id(machinetype, authorization):
    machinetype_id = None
    cloudstack_response = _get_machinetypes(
        authorization,
        args={'keyword': machinetype}
    )

    if cloudstack_response['listserviceofferingsresponse']:
        machinetype_id = cloudstack_response[
            'listserviceofferingsresponse']['serviceoffering'][0]['id']
    return machinetype_id


def _cloudstack_machinetype_to_gce(
        cloudstack_response, selfLink=None, zone=None):
    response = {}
    response['kind'] = 'compute#machineType'
    response['name'] = cloudstack_response['name']
    response['id'] = cloudstack_response['id']
    response['description'] = cloudstack_response['displaytext']
    response['creationTimestamp'] = cloudstack_response['created']
    response['guestCpus'] = cloudstack_response['cpunumber']
    response['memoryMb'] = cloudstack_response['memory']

    if not selfLink:
        response['selfLink'] = request.base_url
    else:
        response['selfLink'] = selfLink

    if not zone:
        response['zone'] = cloudstack_response['zonename']
    else:
        response['zone'] = zone

    return response


@app.route('/' + app.config['PATH'] + '<projectid>/aggregated/machineTypes', methods=['GET'])
@authentication.required
def aggregatedlistmachinetypes(projectid, authorization):
    machine_types = _get_machinetypes(authorization)
    zonelist = zones.get_zone_names(authorization)

    items = {}
    for zone in zonelist:
        zone_machine_types = []
        if machine_types['listserviceofferingsresponse']:
            for machineType in machine_types['listserviceofferingsresponse']['serviceoffering']:
                zone_machine_types.append(
                    _cloudstack_machinetype_to_gce(
                        cloudstack_response=machineType,
                        selfLink=request.base_url + '/' + machineType['name']
                    )
                )
        else:
            zone_machine_types.append(errors.no_results_found(zone))

        items['zone/' + zone] = {}
        items['zone/' + zone]['zone'] = zone
        items['zone/' + zone]['machineTypes'] = zone_machine_types

    populated_response = {
        'kind': 'compute#machineTypeAggregatedList',
        'id': 'projects/' + projectid + '/aggregated/machineTypes',
        'selfLink': request.base_url,
        'items': machine_types
    }
    return helper.createresponse(data=populated_response)


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/machineTypes', methods=['GET'])
@authentication.required
def listmachinetype(projectid, authorization, zone):
    cloudstack_response = _get_machinetypes(authorization)

    machine_types = []
    if cloudstack_response['listserviceofferingsresponse']:
        for service_offering in cloudstack_response['listserviceofferingsresponse']['serviceoffering']:
            machine_types.append(_cloudstack_machinetype_to_gce(service_offering, zone, request.base_url +
                                                                '/' + service_offering['name']))

    populated_response = {
        'kind': 'compute#machineTypeList',
        'id': 'projects/' + projectid + '/aggregated/machineTypes',
        'selfLink': request.base_url,
        'items': machine_types
    }
    return helper.createresponse(data=populated_response)


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/machineTypes/<machinetype>', methods=['GET'])
@authentication.required
def getmachinetype(projectid, authorization, zone, machinetype):
    cloudstack_response = _get_machinetypes(
        authorization,
        args={'keyword': machinetype}
    )
    if cloudstack_response['listserviceofferingsresponse']:
        machinetype = _cloudstack_machinetype_to_gce(
            cloudstack_response['listserviceofferingsresponse']['serviceoffering'][0])
        return helper.createsuccessfulresponse(data=machinetype)

    func_route = url_for('getmachinetype', projectid=projectid, machinetype=machinetype, zone=zone)
    return errors.resource_not_found(func_route)
est(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

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
