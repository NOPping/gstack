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
from flask import jsonify
import json


@app.route('/discovery/v1/apis/compute/v1beta15/rest')
def discovery():
    print app.config['DATA']
    with open(app.config['DATA'] + '/v15beta15.json') as discovery_template_data:
        discovery_template = json.loads(discovery_template_data.read())

    discovery_template['baseUrl'] = 'https://' + app.config['LISTEN_ADDRESS'] + ':' + app.config['LISTEN_PORT']  + '/' + app.config['PATH']
    discovery_template['basePath'] = '/' + app.config['PATH']
    discovery_template['rootUrl'] = 'https://' + app.config['LISTEN_ADDRESS'] + ':' + app.config['LISTEN_PORT'] + '/'
    discovery_template['servicePath'] = app.config['PATH']

    resp = jsonify(discovery_template)

    resp.status_code = 200
    return resp
