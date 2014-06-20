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

from flask import request, url_for

from gstack import app
from gstack import authentication
from gstack import helpers
from gstack import controllers


def _cloudstack_service_offering_to_gce(cloudstack_response, projectid, zone):
    response = {}
    response['kind'] = 'compute#machineType'
    response['name'] = cloudstack_response['name']
    response['id'] = cloudstack_response['id']
    response['description'] = cloudstack_response['displaytext']
    response['creationTimestamp'] = cloudstack_response['created']
    response['guestCpus'] = cloudstack_response['cpunumber']
    response['memoryMb'] = cloudstack_response['memory']

    response['selfLink'] = urllib.unquote_plus(helpers.get_root_url() + url_for(
        'getmachinetype',
        projectid=projectid,
        machinetype=cloudstack_response['name'],
        zone=zone
    ))
    response['zone'] = zone

    return response


def get_machinetype_by_name(authorization, machinetype):
    args = {'command': 'listServiceOfferings'}
    return controllers.get_item_with_name(authorization, machinetype, args, 'serviceoffering')


@app.route('/compute/v1/projects/<projectid>/aggregated/machineTypes', methods=['GET'])
@authentication.required
def aggregatedlistmachinetypes(projectid, authorization):
    args = {'command': 'listServiceOfferings'}
    kwargs = {'projectid': projectid}
    items = controllers.describe_items_aggregated(
        authorization, args, 'serviceoffering', 'machineTypes',
        _cloudstack_service_offering_to_gce, **kwargs)

    populated_response = {
        'kind': 'compute#machineTypeAggregatedList',
        'id': 'projects/' + projectid + '/aggregated/machineTypes',
        'selfLink': urllib.unquote_plus(request.base_url),
        'items': items
    }
    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/machineTypes', methods=['GET'])
@authentication.required
def listmachinetype(projectid, authorization, zone):
    args = {'command': 'listServiceOfferings'}
    kwargs = {'projectid': projectid, 'zone': zone}
    items = controllers.describe_items(
        authorization, args, 'serviceoffering',
        _cloudstack_service_offering_to_gce, **kwargs)

    populated_response = {
        'kind': 'compute#imageList',
        'selfLink': urllib.unquote_plus(request.base_url),
        'id': 'projects/' + projectid + '/global/images',
        'items': items
    }

    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/machineTypes/<machinetype>', methods=['GET'])
@authentication.required
def getmachinetype(projectid, authorization, zone, machinetype):
    func_route = url_for('getmachinetype', projectid=projectid, zone=zone, machinetype=machinetype)
    args = {'command': 'listServiceOfferings'}
    kwargs = {'projectid': projectid, 'zone': zone}
    return controllers.get_item_with_name_or_error(
        authorization, machinetype, args, 'serviceoffering', func_route,
        _cloudstack_service_offering_to_gce, **kwargs)
