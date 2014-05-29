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


from gstack import app
from gstack import authentication
from gstack.services import requester
from gstack.controllers import errors, helper
from flask import request, url_for


def _get_regions(authorization, args=None):
    command = 'listRegions'
    if not args:
        args = {}

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    return cloudstack_response


def _cloudstack_region_to_gce(response_item):
    response = {}
    response['kind'] = 'compute#region'
    response['description'] = response_item['name']
    response['id'] = response_item['id']
    response['status'] = 'UP'
    return response


@app.route('/compute/v1/projects/<projectid>/regions', methods=['GET'])
@authentication.required
def listregions(projectid, authorization):
    cloudstack_response = _get_regions(authorization)

    regions = []

    if cloudstack_response['listregionsresponse']:
        for region in cloudstack_response['listregionsresponse']['region']:
            regions.append(_cloudstack_region_to_gce(region))

    populated_response = {
        'kind': 'compute#regionList',
        'id': 'projects/' + projectid + '/regions',
        'selfLink': request.base_url,
        'items': regions
    }
    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/regions/<region>', methods=['GET'])
@authentication.required
def getregion(projectid, authorization, region):
    cloudstack_response = _get_regions(
        authorization=authorization,
        args={'name': region}
    )

    if cloudstack_response['listregionsresponse']:
        cloudstack_response = _cloudstack_region_to_gce(
            cloudstack_response['listregionsresponse']['region'][0])
        return helper.create_response(data=cloudstack_response)

    function_route = url_for('getimage', projectid=projectid, image=region)
    return errors.resource_not_found(function_route)
