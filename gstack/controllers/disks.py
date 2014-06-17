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
from gstack import app, authentication
from gstack.services import requester
from gstack import helpers
from gstack import controllers
from gstack.controllers import zones, errors


def _cloudstack_volume_to_gce(cloudstack_response, projectid, zone):
    response = {}
    response['kind'] = 'compute#disk'
    response['id'] = cloudstack_response['id']
    response['creationTimestamp'] = cloudstack_response['created']
    response['status'] = cloudstack_response['state'].upper()
    response['name'] = cloudstack_response['name']
    response['description'] = cloudstack_response['name']
    response['sizeGb'] = cloudstack_response['size']

    response['selfLink'] = urllib.unquote_plus(helpers.get_root_url() + url_for(
        'getmachinetype',
        projectid=projectid,
        machinetype=cloudstack_response['name'],
        zone=zone
    ))

    if not zone:
        response['zone'] = cloudstack_response['zonename']
    else:
        response['zone'] = zone

    return response


@app.route('/compute/v1/projects/<projectid>/aggregated/disks', methods=['GET'])
@authentication.required
def aggregatedlistdisks(projectid, authorization):
    args = {'command':'listVolumes'}
    items = controllers.describe_items_aggregated(
        authorization, args, 'volume',
        projectid, _cloudstack_volume_to_gce)

    populated_response = {
        'kind': 'compute#diskAggregatedList',
        'selfLink': urllib.unquote_plus(request.base_url),
        'id': 'projects/' + projectid + '/global/images',
        'items': items
    }

    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/disks', methods=['GET'])
@authentication.required
def listdisks(projectid, authorization, zone):
    args = {'command':'listVolumes'}
    items = controllers.describe_items(
        authorization, args, 'volume',
        projectid, zone, _cloudstack_volume_to_gce)

    populated_response = {
        'kind': 'compute#imageList',
        'selfLink': urllib.unquote_plus(request.base_url),
        'id': 'projects/' + projectid + '/global/images',
        'items': items
    }

    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/disks/<disk>', methods=['GET'])
@authentication.required
def getdisk(projectid, authorization, zone, disk):
    response = get_disk_by_name(
        authorization=authorization,
        disk=disk
    )

    if response:
        return helpers.create_response(
            data=_cloudstack_volume_to_gce(
                cloudstack_response=response,
                projectid=projectid,
                zone=zone
            )
        )
    else:
        func_route = url_for(
            'getdisk',
            projectid=projectid,
            zone=zone,
            disk=disk
        )
        return errors.resource_not_found(func_route)
