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
from flask import jsonify
import json


@app.route('/' + app.config['PATH'] + '<projectid>/global/images',
           methods=['GET'])
@authentication.required
def listimages(projectid, authorization):
    command = 'listTemplates'
    args = {
        'templatefilter': 'all'
    }
    logger = None

    cloudstack_response = requester.make_request(
        command,
        args,
        logger,
        authorization.jsessionid,
        authorization.sessionkey
    )

    cloudstack_response = json.loads(cloudstack_response)
    cloudstack_response = cloudstack_response['listtemplatesresponse']

    templates = []

    translate_status = {
        'True': 'Ready',
        'False': 'Failed'
    }

    # test for empty response, i.e no templates available
    if cloudstack_response:
        for template in cloudstack_response['template']:
            templates.append({
                'kind': "compute#image",
                'selfLink': '',
                'id': template['id'],
                'creationTimestamp': template['created'],
                'name': template['name'],
                'description': template['displaytext'],
                'sourceType': '',
                'preferredKernel': '',
                'rawDisk': {
                    'containerType': template['format'],
                    'source': '',
                    'sha1Checksum': template['checksum'],
                },
                'deprecated': {
                    'state': '',
                    'replacement': '',
                    'deprecated': '',
                    'obsolete': '''
                     'deleted': '''
                },
                'status': translate_status[str(template['isready'])],
            })

    populated_response = {
        'kind': 'compute#imageList',
        'selfLink': '',
        'id': 'blah',
        'items': templates
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
    logger = None

    cloudstack_response = requester.make_request(
        command,
        args,
        logger,
        authorization.jsessionid,
        authorization.sessionkey
    )

    response = json.loads(cloudstack_response)
    template = response['listtemplatesresponse']['template'][0]

    translate_status = {
        'True': 'Ready',
        'False': 'Failed'
    }

    # test for empty response, i.e no templates available
    if cloudstack_response:
        image = {'kind': "compute#image",
                 'selfLink': '',
                 'id': template['id'],
                 'creationTimestamp': template['created'],
                 'name': template['name'],
                 'description': template['displaytext'],
                 'sourceType': '',
                 'preferredKernel': '',
                 'rawDisk': {
                     'containerType': template['format'],
                     'source': '',
                     'sha1Checksum': template['checksum'],
                 },
                 'deprecated': {
                     'state': '',
                     'replacement': '',
                     'deprecated': '',
                     'obsolete': '',
                     'deleted': ''
                 },
                 'status': translate_status[str(template['isready'])],
                 }

    res = jsonify(image)
    res.status_code = 200
    return res


@app.route('/' + app.config['PATH'] + '<projectid>/global/images/<image>',
           methods=['DELETE'])
@authentication.required
def deleteimage(projectid, authorization, image):
    command = 'deleteTemplate'
    #should be something like: imageid = _get_template_id(image)
    # this needs to call getimage() and return the image id
    imageid = image
    args = {
        'id': imageid
    }
    logger = None

    cloudstack_response = requester.make_request(
        command,
        args,
        logger,
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
