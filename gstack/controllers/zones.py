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

from gstack import helpers
from gstack import controllers
from gstack import app, authentication
from gstack.services import requester


def _get_zones(authorization):
    command = 'listZones'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    return cloudstack_response


def _cloudstack_zone_to_gce(cloudstack_response):
    return ({
        'kind': 'compute#zone',
        'name': cloudstack_response['name'],
        'description': cloudstack_response['name'],
        'id': cloudstack_response['id'],
        'status': cloudstack_response['allocationstate']
    })


def get_zone_by_name(authorization, zone):
    args = {'command': 'listZones'}
    return controllers.get_item_with_name(authorization, zone, args, 'zone')


def get_zone_names(authorization):
    zone_list = _get_zones(authorization)

    zones = []
    if zone_list['listzonesresponse']:
        for zone in zone_list['listzonesresponse']['zone']:
            zones.append(zone['name'])

    return zones


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

    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/zones/<zone>', methods=['GET'])
@authentication.required
def getzone(projectid, authorization, zone):
    func_route = url_for('getzone', projectid=projectid, zone=zone)
    args = {'command': 'listZones'}
    return controllers.get_item_with_name_or_error(
        authorization, zone, args, 'zone', func_route,
        _cloudstack_zone_to_gce, **{})
