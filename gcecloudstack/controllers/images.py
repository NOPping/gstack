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
from flask import jsonify, request
import json


@app.route('/' + app.config['PATH'] + 'centos-cloud/global/images',
           methods=['GET'])
@authentication.required
def listnocentoscloudimages(authorization):
    res = jsonify({
        "kind": "compute#imageList",
        "selfLink": "",
        "id": "projects/centos-cloud/global/images"
    })
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + 'debian-cloud/global/images',
           methods=['GET'])
@authentication.required
def listnodebiancloudimages(authorization):
    res = jsonify({
        "kind": "compute#imageList",
        "selfLink": "",
        "id": "projects/debian-cloud/global/images"
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
    cloudstack_responses = cloudstack_response['listtemplatesresponse']

    images = []

    translate_image_status = {
        'True': 'Ready',
        'False': 'Failed'
    }

    # test for response, i.e are templates available
    if cloudstack_responses:
        for cloudstack_response in cloudstack_responses['template']:
            images.append({
                'kind': "compute#image",
                'selfLink': request.base_url + '/' + cloudstack_response['name'],
                'id': cloudstack_response['id'],
                'creationTimestamp': cloudstack_response['created'],
                'name': cloudstack_response['name'],
                'description': cloudstack_response['displaytext'],
                'sourceType': '',
                'preferredKernel': '',
                'rawDisk': {
                    'containerType': cloudstack_response['format'],
                    'source': '',
                    'sha1Checksum': cloudstack_response['checksum'],
                },
                'deprecated': {
                    'state': '',
                    'replacement': '',
                    'deprecated': '',
                    'obsolete': '',
                    'deleted': ''
                },
                'status': translate_image_status[str(cloudstack_response[
                    'isready'
                ])],
            })

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

    translate_image_status = {
        'True': 'Ready',
        'False': 'Failed'
    }

    cloudstack_response = json.loads(cloudstack_response)
    if cloudstack_response['listtemplatesresponse']:
        cloudstack_response = cloudstack_response['listtemplatesresponse']['template'][0]
        image = {
            'kind': "compute#image",
            'selfLink': request.base_url,
            'id': cloudstack_response['id'],
            'creationTimestamp': cloudstack_response['created'],
            'name': cloudstack_response['name'],
            'description': cloudstack_response['displaytext'],
            'sourceType': '',
            'preferredKernel': '',
            'rawDisk': {
                'containerType': cloudstack_response['format'],
                'source': '',
                'sha1Checksum': cloudstack_response['checksum'],
            },
            'deprecated': {
                'state': '',
                         'replacement': '',
                         'deprecated': '',
                         'obsolete': '',
                         'deleted': ''
            },
            'status': translate_image_status[str(cloudstack_response[
                'isready'
            ])],
        }
        res = jsonify(image)
        res.status_code = 200
    else:
        res = jsonify({
            'error': {
                'errors': [
                    {
                        "domain": "global",
                        "reason": "notFound",
                        "message": 'The resource \'projects/' + projectid + '/global/images/' + image + '\' was not found'
                    }
                ],
                'code': 404,
                'message': 'The resource \'projects/' + projectid + '/global/images/' + image + '\' was not found'
            }
        })
        res.status_code = 404

    return res


@app.route('/' + app.config['PATH'] + '<projectid>/global/images/<image>',
           methods=['DELETE'])
@authentication.required
def deleteimage(projectid, authorization, image):
    command = 'deleteTemplate'
    # should be something like: imageid = _get_template_id(image)
    # this needs to call getimage() and return the image id
    imageid = image
    args = {
        'id': imageid
    }

    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.jsessionid,
        authorization.sessionkey
    )

    res = json.loads(cloudstack_response)['deletetemplateresponse']

    globalops = {"kind": "compute#operation",
                 "id": imageid,
                 "creationTimestamp": '',
                 "name": image,
                 "zone": '',
                 "clientOperationId": '',
                 "operationType": 'delete',
                 "targetLink": '',
                 "targetId": 'unsigned long',
                 "status": res['success'],
                 "statusMessage": res['displaytext'],
                 "user": '',
                 "progress": '',
                 "insertTime": '',
                 "startTime": '',
                 "endTime": '',
                 "error": {
                     "errors": [
                         {
                             "code": '',
                             "location": '',
                             "message": ''
                         }
                     ]
                 },
                 "warnings": [
                     {
                         "code": '',
                         "message": '',
                         "data": [{"key": '', "value": ''}]
                     }
                 ],
                 "httpErrorStatusCode": '',
                 "httpErrorMessage": '',
                 "selfLink": '',
                 "region": ''
                 }

    res = jsonify(globalops)
    res.status_code = 200
    return res
