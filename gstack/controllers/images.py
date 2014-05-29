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
from gstack import app, authentication
from gstack.services import requester
from gstack.controllers import helper, errors
from flask import request, url_for


def _get_templates(authorization, args=None):
    command = 'listTemplates'
    if not args:
        args = {}

    if 'templatefilter' not in args:
        args['templatefilter'] = 'executable'

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    return cloudstack_response


def get_template_by_name(authorization, image):
    image_list = _get_templates(
        authorization=authorization,
        args={
            'keyword': image
        }
    )

    if image_list['listtemplatesresponse']:
        response = helper.filter_by_name(
            data=image_list['listtemplatesresponse']['template'],
            name=image
        )
        return response
    else:
        return None


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


def _cloudstack_template_to_gce(cloudstack_response, selfLink=None):
    translate_image_status = {
        'True': 'Ready',
        'False': 'Failed'
    }

    response = {}
    response['kind'] = 'compute#image'
    response['id'] = cloudstack_response['id']
    response['creationTimestamp'] = cloudstack_response['created']
    response['name'] = cloudstack_response['name']
    response['description'] = cloudstack_response['displaytext']
    response['status'] = translate_image_status[
        str(cloudstack_response['isready'])]

    if selfLink:
        response['selfLink'] = urllib.unquote_plus(selfLink)
    else:
        response['selfLink'] = urllib.unquote_plus(request.base_url)

    return response


@app.route('/compute/v1/projects/centos-cloud/global/images', methods=['GET'])
@authentication.required
def listnocentoscloudimages(authorization):
    populated_response = _create_populated_image_response('centos-cloud')
    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/debian-cloud/global/images', methods=['GET'])
@authentication.required
def listnodebiancloudimages(authorization):
    populated_response = _create_populated_image_response('debian-cloud')
    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/global/images', methods=['GET'])
@authentication.required
def listimages(projectid, authorization):
    image_list = _get_templates(
        authorization=authorization
    )

    images = []
    if image_list['listtemplatesresponse']:
        for image in image_list['listtemplatesresponse']['template']:
            images.append(_cloudstack_template_to_gce(
                cloudstack_response=image,
                selfLink=request.base_url + '/' + image['name']))

    populated_response = _create_populated_image_response(projectid, images)
    return helper.create_response(data=populated_response)


@app.route('/compute/v1/projects/<projectid>/global/images/<image>', methods=['GET'])
@authentication.required
def getimage(projectid, authorization, image):
    response = get_template_by_name(
        authorization=authorization,
        image=image
    )

    if response:
        return helper.create_response(
            data=_cloudstack_template_to_gce(response)
        )
    else:
        func_route = url_for('getimage', projectid=projectid, image=image)
        return errors.resource_not_found(func_route)
