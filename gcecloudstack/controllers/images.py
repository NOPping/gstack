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
from gcecloudstack.controllers import errors
from flask import jsonify, request, url_for
import json


def _get_template_id(image, authorization):
    command = 'listTemplates'
    args = {
        'templatefilter': 'all',
        'keyword': image
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )
    template_id = None
    cloudstack_responses = json.loads(cloudstack_response)
    if cloudstack_responses['listtemplatesresponse']:
        template_id = cloudstack_responses[
            'listtemplatesresponse']['template'][0]['id']
    return template_id


def _cloudstack_image_to_gce(response_item):
    translate_image_status = {
        'True': 'Ready',
        'False': 'Failed'
    }

    return ({
        'kind': 'compute#image',
        'selfLink': request.base_url + '/' + response_item['name'],
        'id': response_item['id'],
        'creationTimestamp': response_item['created'],
        'name': response_item['name'],
        'description': response_item['displaytext'],
        'sourceType': 'RAW',
        'preferredKernel': '',
        'rawDisk': {
                'containerType': response_item['format'],
                'source': '',
                'sha1Checksum': response_item['checksum'],
        },
        'status': translate_image_status[str(response_item['isready'])],
    })


def _cloudstack_delete_to_gce(cloudstack_response, image, imageid):
    return({
        'kind': 'compute#operation',
        'id': imageid,
        'creationTimestamp': '',
        'name': image,
        'zone': '',
        'clientOperationId': '',
        'operationType': 'delete',
        'targetLink': '',
        'targetId': 'unsigned long',
        'status': cloudstack_response['success'],
        'statusMessage': cloudstack_response['displaytext'],
        'user': '',
        'progress': '',
        'insertTime': '',
        'startTime': '',
        'endTime': '',
        'error': {
            'errors': [
                {
                     'code': '',
                     'location': '',
                     'message': ''
                }
            ]
        },
        'warnings': [
            {
                'code': '',
                'message': '',
                'data': [{'key': '', 'value': ''}]
            }
        ],
        'httpErrorStatusCode': '',
        'httpErrorMessage': '',
        'selfLink': '',
        'region': ''
    })


@app.route('/' + app.config['PATH'] + 'centos-cloud/global/images',
           methods=['GET'])
@authentication.required
def listnocentoscloudimages(authorization):
    res = jsonify({
        'kind': 'compute#imageList',
        'selfLink': request.base_url,
        'id': 'projects/centos-cloud/global/images'
    })
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + 'debian-cloud/global/images',
           methods=['GET'])
@authentication.required
def listnodebiancloudimages(authorization):
    res = jsonify({
        'kind': 'compute#imageList',
        'selfLink': request.base_url,
        'id': 'projects/debian-cloud/global/images'
    })
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/global/images',
           methods=['GET'])
@authentication.required
def listimages(projectid, authorization):
    command = 'listTemplates'
    args = {
        'templatefilter': 'all'
    }

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        'Processing request for list images\n'
        'Project: ' + projectid + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    images = []
    if cloudstack_response['listtemplatesresponse']:
        for response_item in cloudstack_response[
                'listtemplatesresponse']['template']:
            images.append(_cloudstack_image_to_gce(response_item))

    populated_response = {
        'kind': 'compute#imageList',
        'selfLink': request.base_url,
        'id': 'projects/' + projectid + '/global/images',
        'items': images
    }
    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/global/images/<image>',
           methods=['GET'])
@authentication.required
def getimage(projectid, authorization, image):
    command = 'listTemplates'
    args = {
        'templatefilter': 'all',
        'keyword': image
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )
    cloudstack_response = json.loads(cloudstack_response)

    app.logger.debug(
        'Processing request for get image\n'
        'Project: ' + projectid + '\n' +
        'Image: ' + image + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    if cloudstack_response['listtemplatesresponse']:
        response_item = cloudstack_response[
            'listtemplatesresponse']['template'][0]
        image = _cloudstack_image_to_gce(response_item)
        res = jsonify(image)
        res.status_code = 200
    else:
        func_route = url_for('getimage', projectid=projectid, image=image)
        res = errors.resource_not_found(func_route)

    return res


@app.route('/' + app.config['PATH'] + '<projectid>/global/images/<image>',
           methods=['DELETE'])
@authentication.required
def deleteimage(projectid, authorization, image):
    command = 'deleteTemplate'
    imageid = _get_template_id(image, authorization)
    if imageid is None:
        func_route = url_for('deleteimage', projectid=projectid, image=image)
        return(errors.resource_not_found(func_route))

    args = {
        'id': imageid
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )
    image_deleted = _cloudstack_delete_to_gce(
        cloudstack_response,
        image,
        imageid
    )

    res = jsonify(image_deleted)
    res.status_code = 200
    return res
