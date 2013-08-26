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
from flask import jsonify, Response

"""
Method	HTTP request	                 Description
get	GET  /project/regions/region	 Returns the specified region resource.
list	GET  /project/regions	         Retrieves the list of region resources available to the specified project.
"""

import gcecloudstack.services.requester as requester


def _to_region_id():
    '''
    To be implemented, get region id from region parameter from GCE
    '''

# this is just an example to show how to use different http verbs


@app.route('/project/regions', methods=['GET'])
def regions(region):
    response, error = requester.make_request('listLocations', None, None, app.config['HOST'], app.config[
                                             'PORT'], app.config['API_KEY'], app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
    return response


@app.route('/project/regions/<region>', methods=['GET'])
def region(region):
    regionid = _to_region_id(region)
    response, error = requester.make_request('listLocations', {'id': regionid}, None, app.config['HOST'], app.config[
                                             'PORT'], app.config['API_KEY'], app.config['SECRET_KEY'], app.config['PROTOCOL'], app.config['PATH'])
    return response
