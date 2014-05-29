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
from gstack.controllers import zones, helper, errors


def _get_disks(authorization, args=None):
    command = 'listVolumes'
    if not args:
        args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def get_disk_by_name(authorization, disk):
    disk_list = _get_disks(
        authorization=authorization,
        args={
            'keyword': disk
        }
    )

    if disk_list['listvolumesresponse']:
        response = helper.filter_by_name(
            data=disk_list['listvolumesresponse']['volume'],
            name=disk
        )
        return response
    else:
        return None


def _cloudstack_volume_to_gce(cloudstack_response, projectid, zone):
    response = {}
    response['kind'] = 'compute#disk'
    response['id'] = cloudstack_response['id']
    response['creationTimestamp'] = cloudstack_response['created']
    response['status'] = cloudstack_response['state'].upper()
    response['name'] = cloudstack_response['name']
    response['description'] = cloudstack_response['name']
    response['sizeGb'] = cloudstack_response['size']

    response['selfLink'] = urllib.unquote_plus(helper.get_root_url() + url_for(
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
    disk_list = _get_disks(authorization=authorization)
    zone_list = zones.get_zone_names(authorization=authorization)

    disk = None
    filter = helper.get_filter(request.args)

    if 'name' in filter:
        disk = filter['name']

    items = {}

    for zone in zone_list:
        zone_disks = []
        if disk:
            disk = get_disk_by_name(
                authorization=authorization,
                disk=disk
            )
            if disk:
                zone_disks.append(
                    _cloudstack_volume_to_gce(
                        cloudstack_response=disk,
                        projectid=projectid,
                        zone=zone,
                    )
                )

        elif disk_list['listvolumesresponse']:
            for disk in disk_list['listvolumesresponse']['volume']:
                zone_disks.append(
                    _cloudstack_volume_to_gce(
                        cloudstack_response=disk,
                        projectid=projectid,
                        zone=zone,
                    )
                )
        items['zone/' + zone] = {}
        items['zone/' + zone]['disks'] = zone_disks

    populated_response = {
        'kind': 'compute#diskAggregatedList',
        'selfLink': urllib.unquote_plus(request.base_url),
        'id': 'projects/' + projectid + '/global/images',
        'items': items
    }

    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/disks', methods=['GET'])
@authentication.required
def listdisks(projectid, authorization, zone):
    disk = None
    filter = helper.get_filter(request.args)

    if 'name' in filter:
        disk = filter['name']

    items = []

    if disk:
        disk_list = _get_disks(
            authorization=authorization,
            args={'keyword': disk}
        )
        if disk_list['listvolumesresponse']:
            disk = helper.filter_by_name(
                data=disk_list['listvolumesresponse']['volume'],
                name=disk
            )
            if disk:
                items.append(
                    _cloudstack_volume_to_gce(
                        cloudstack_response=disk,
                        projectid=projectid,
                        zone=zone
                    )
                )
    else:
        disk_list = _get_disks(authorization=authorization)
        if disk_list['listvolumesresponse']:
            for disk in disk_list['listvolumesresponse']['volume']:
                items.append(
                    _cloudstack_volume_to_gce(
                        cloudstack_response=disk,
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


@app.route('/compute/v1/projects/<projectid>/zones/<zone>/disks/<disk>', methods=['GET'])
@authentication.required
def getdisk(projectid, authorization, zone, disk):
    response = get_disk_by_name(
        authorization=authorization,
        disk=disk
    )

    if response:
        return helper.create_response(
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
            disk=disk
        )
        return errors.resource_not_found(func_route)
