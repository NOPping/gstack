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
from gstack.controllers import helper
import json


@app.route('/discovery/v1/apis/compute/v1/rest', methods=['GET'])
def discovery():
    with open(app.config['DATA'] + '/v1.json') as template:
        discovery_template = json.loads(template.read())

    discovery_template[
        'baseUrl'] = helper.get_root_url() + '/' + app.config['PATH']
    discovery_template['basePath'] = '/' + app.config['PATH']
    discovery_template['rootUrl'] = helper.get_root_url() + '/'
    discovery_template['servicePath'] = app.config['PATH']

    return helper.create_response(data=discovery_template)
