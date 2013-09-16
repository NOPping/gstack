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


def _cloudstack_volume_to_gce(response_item):
    return {
        "kind": "compute#disk",
        "selfLink": request.base_url + '/' + response_item['name'],
        "id": response_item['id'],
        "creationTimestamp": response_item['created'],
        "zone": response_item['zonename'],
        "status": response_item['state'],
        "name": response_item['name'],
        "description": response_item['name'],
        "sizeGb": response_item['size'],
        "sourceSnapshot": '',
        "sourceSnapshotId": '',
        "sourceImage": ''
    }


@app.route('/' + app.config['PATH'] + '<projectid>/aggregated/disks',
           methods=['GET'])
@authentication.required
def aggregatedlistdisks(projectid, authorization):
    command = 'listVolumes'
    args = {}

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        'Processing request for list disks\n'
        'Project: ' + projectid + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    disks = []
    if cloudstack_response['listvolumesresponse']:
        for response_item in cloudstack_response[
                'listvolumesresponse']['volume']:
            disks.append(_cloudstack_volume_to_gce(response_item))

    zonelist = zones.get_zone_names(authorization)

    items = {}
    for zone in zonelist:
        zone_disks = []
        for disk in disks:
            disk['zone'] = zone
            disk['selfLink'] = request.base_url + \
                '/' + disk['name']
            zone_disks.append(disk)

        items['zone/' + zone] = {}
        items['zone/' + zone]['zone'] = zone
        items['zone/' + zone]['disks'] = zone_disks

    populated_response = {
        'kind': 'compute#diskAggregatedList',
        'selfLink': request.base_url,
        'id': 'projects/' + projectid + '/global/images',
        'items': items
    }
    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/zones/<zone>/disks',
           methods=['GET'])
@authentication.required
def listdisks(projectid, authorization, zone):
    command = 'listVolumes'
    args = {}

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        'Processing request for list disks\n'
        'Project: ' + projectid + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    disks = []
    if cloudstack_response['listvolumesresponse']:
        for response_item in cloudstack_response[
                'listvolumesresponse']['volume']:
            disks.append(_cloudstack_volume_to_gce(response_item))

    populated_response = {
        'kind': 'compute#imageList',
        'selfLink': request.base_url,
        'id': 'projects/' + projectid + '/global/images',
        'items': disks
    }
    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] +
           '<projectid>/zones/<zone>/disks', methods=['POST'])
@authentication.required
def insertdisk(projectid, authorization, zone):
    image_url = (json.loads(request.data))['description']
    url_sections = image_url.split('/')
    image_name = url_sections[-1]

    command = 'createVolume'
    args = {
        'name': image_name
    }

    # At the minute we're returning a spoofed response without creating a
    # volume

    # cloudstack_response = requester.make_request(
    #    command,
    #    args,
    #    authorization.jsessionid,
    #    authorization.sessionkey
    # )

    populated_response = {
        "kind": "compute#disk",
        "selfLink": request.base_url,
        "id": 0,
        "creationTimestamp": '',
        "zone": '',
        "status": '',
        "name": '',
        "description": '',
        "sizeGb": 100,
        "sourceSnapshot": '',
        "sourceSnapshotId": '',
        "sourceImage": ''
    }
    res = jsonify(populated_response)
    res.status_code = 200
    return res
