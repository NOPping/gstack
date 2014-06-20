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
from gstack import helpers
from gstack import controllers


def _create_populated_image_response(projectid, images=None):
    if not images:
        images = []

    populated_response = {
        'kind': 'compute#imageList',
        'selfLink': request.base_url,
        'id': 'projects/' + projectid + '/global/images',
        'items': images
    }
    return populated_response


def _cloudstack_template_to_gce(cloudstack_response):
    response = {}
    response['kind'] = 'compute#image'
    response['id'] = cloudstack_response['id']
    response['creationTimestamp'] = cloudstack_response['created']
    response['name'] = cloudstack_response['name']
    response['description'] = cloudstack_response['displaytext']
    response['status'] = cloudstack_response['isready']
    response['selfLink'] = urllib.unquote_plus(request.base_url) + '/' + response['name']

    return response


def get_template_by_name(authorization, image):
    args = {'templatefilter': 'executable', 'command': 'listTemplates'}
    return controllers.get_item_with_name(authorization, image, args, 'template')


@app.route('/compute/v1/projects/centos-cloud/global/images', methods=['GET'])
@authentication.required
def listnocentoscloudimages(authorization):
    populated_response = _create_populated_image_response('centos-cloud')
    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/debian-cloud/global/images', methods=['GET'])
@authentication.required
def listnodebiancloudimages(authorization):
    populated_response = _create_populated_image_response('debian-cloud')
    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/global/images', methods=['GET'])
@authentication.required
def listimages(projectid, authorization):
    args = {'templatefilter': 'executable', 'command': 'listTemplates'}
    items = controllers.describe_items(
        authorization, args, 'template',
        _cloudstack_template_to_gce, **{})

    populated_response = _create_populated_image_response(projectid, items)
    return helpers.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/global/images/<image>', methods=['GET'])
@authentication.required
def getimage(projectid, authorization, image):
    func_route = url_for('getimage', projectid=projectid, image=image)
    args = {'templatefilter': 'executable', 'command': 'listTemplates'}
    return controllers.get_item_with_name_or_error(
        authorization, image, args, 'template', func_route,
        _cloudstack_template_to_gce, **{})
