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

from gstack import app
from gstack import helpers
from gstack import controllers
from gstack import authentication


def _cloudstack_account_to_gce(cloudstack_response):
    response = {}
    response['kind'] = 'compute#region'
    response['description'] = cloudstack_response['name']
    response['name'] = cloudstack_response['name']
    response['id'] = cloudstack_response['id']
    response['status'] = 'UP'
    return response


@app.route('/compute/v1/projects/<projectid>/regions', methods=['GET'])
@authentication.required
def listregions(projectid, authorization):
    args = {'command': 'listRegions'}
    kwargs = {}
    items = controllers.describe_items(
        authorization, args, 'region',
        _cloudstack_account_to_gce, **kwargs)

    populated_response = {
        'kind': 'compute#regionList',
        'id': 'projects/' + projectid + '/regions',
        'selfLink': request.base_url,
        'items': items
    }
    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/regions/<region>', methods=['GET'])
@authentication.required
def getregion(projectid, authorization, region):
    func_route = url_for('getregion', projectid=projectid, region=region)
    args = {'command': 'listRegions'}
    return controllers.get_item_with_name_or_error(
        authorization, region, args, 'region', func_route,
        _cloudstack_account_to_gce, **{})
