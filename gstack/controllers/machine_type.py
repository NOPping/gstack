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
from gstack import app
from gstack import authentication
from gstack.services import requester
from gstack.controllers import errors, zones, helper
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


def get_machinetype_by_name(authorization, machinetype):
    machinetype_list = _get_machinetypes(
        authorization=authorization
    )

    if machinetype_list['listserviceofferingsresponse']:
        response = helper.filter_by_name(
            data=machinetype_list['listserviceofferingsresponse'][
                'serviceoffering'],
            name=machinetype
        )
        return response
    else:
        return None


def _cloudstack_machinetype_to_gce(cloudstack_response, projectid, zone):
    response = {}
    response['kind'] = 'compute#machineType'
    response['name'] = cloudstack_response['name']
    response['id'] = cloudstack_response['id']
    response['description'] = cloudstack_response['displaytext']
    response['creationTimestamp'] = cloudstack_response['created']
    response['guestCpus'] = cloudstack_response['cpunumber']
    response['memoryMb'] = cloudstack_response['memory']

    response['selfLink'] = urllib.unquote_plus(helper.get_root_url() + url_for(
        'getmachinetype',
        projectid=projectid,
        machinetype=cloudstack_response['name'],
        zone=zone
    ))
    response['zone'] = zone

    return response


@app.route('/compute/v1/projects/<projectid>/aggregated/machineTypes', methods=['GET'])
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
                        projectid=projectid,
                        zone=zone
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
        'selfLink': urllib.unquote_plus(request.base_url),
        'items': items
    }
    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/machineTypes', methods=['GET'])
@authentication.required
def listmachinetype(projectid, authorization, zone):
    machinetype = None
    filter = helper.get_filter(request.args)

    if 'name' in filter:
        machinetype = filter['name']

    items = []

    if machinetype:
        machinetype_list = _get_machinetypes(
            authorization=authorization,
            args={'keyword': machinetype}
        )
        if machinetype_list['listvolumesresponse']:
            machinetype = helper.filter_by_name(
                data=machinetype_list['listserviceofferingsresponse'][
                    'serviceoffering'],
                name=machinetype
            )
            if machinetype:
                items.append(
                    _cloudstack_machinetype_to_gce(
                        cloudstack_response=machinetype,
                        projectid=projectid,
                        zone=zone
                    )
                )
    else:
        machinetype_list = _get_machinetypes(authorization=authorization)
        if machinetype_list['listserviceofferingsresponse']:
            for machinetype in machinetype_list['listserviceofferingsresponse']['serviceoffering']:
                items.append(
                    _cloudstack_machinetype_to_gce(
                        cloudstack_response=machinetype,
                        projectid=projectid,
                        zone=zone
                    )
                )

    populated_response = {
        'kind': 'compute#imageList',
        'selfLink': urllib.unquote_plus(request.base_url),
        'id': 'projects/' + projectid + '/global/images',
        'items': items
    }

    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/machineTypes/<machinetype>', methods=['GET'])
@authentication.required
def getmachinetype(projectid, authorization, zone, machinetype):
    response = get_machinetype_by_name(
        authorization=authorization,
        machinetype=machinetype
    )

    if response:
        return helper.create_response(
            data=_cloudstack_machinetype_to_gce(
                cloudstack_response=response,
                projectid=projectid,
                zone=zone
            )
        )
    else:
        func_route = url_for(
            'getmachinetype',
            projectid=projectid,
            machinetype=machinetype,
            zone=zone)
        return errors.resource_not_found(func_route)
