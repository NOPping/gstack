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

from flask import request, url_for
from gstack import app, authentication
from gstack.services import requester
from gstack.controllers import helper, errors


def _get_zones(authorization, args=None):
    command = 'listZones'
    if not args:
        args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def get_zone_by_name(authorization, zone):
    zone_list = _get_zones(
        authorization=authorization,
        args={
            'keyword': zone
        }
    )

    if zone_list['listzonesresponse']:
        response = helper.filter_by_name(
            data=zone_list['listzonesresponse']['zone'],
            name=zone
        )
        return response
    else:
        return None


def get_zone_names(authorization):
    zone_list = _get_zones(authorization)

    zones = []
    if zone_list['listzonesresponse']:
        for zone in zone_list['listzonesresponse']['zone']:
            zones.append(zone['name'])

    return zones


def _cloudstack_zone_to_gce(response_item):
    translate_zone_status = {
        'Enabled': 'UP',
        'Disabled': 'DOWN'
    }
    return ({
        'kind': 'compute#zone',
        'name': response_item['name'],
        'description': response_item['name'],
        'id': response_item['id'],
        'status': translate_zone_status[str(response_item['allocationstate'])]
    })


@app.route('/compute/v1/projects/<projectid>/zones', methods=['GET'])
@authentication.required
def listzones(projectid, authorization):
    zone_list = _get_zones(authorization)

    items = []
    if zone_list['listzonesresponse']:
        for zone in zone_list['listzonesresponse']['zone']:
            items.append(_cloudstack_zone_to_gce(zone))

    populated_response = {
        'kind': 'compute#zoneList',
        'id': 'projects/' + projectid + '/zones',
        'selfLink': request.base_url,
        'items': items
    }

    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>', methods=['GET'])
@authentication.required
def getzone(projectid, authorization, zone):
    response = get_zone_by_name(
        authorization=authorization,
        zone=zone
    )

    if response:
        return helper.create_response(
            data=_cloudstack_zone_to_gce(response)
        )
    else:
        func_route = url_for('getzone', projectid=projectid, zone=zone)
        return errors.resource_not_found(func_route)
