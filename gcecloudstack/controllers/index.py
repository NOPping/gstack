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
import os


@app.route('/discovery/v1/apis/compute/v1beta15/rest')
def discovery():

    basepath = os.path.dirname(__file__)
    discovery_template = open(
        os.path.join(
            basepath,
            "..",
            "templates/discovery.json"
        ), "r"
    )
    discovery_template = json.loads(discovery_template.read())
    resp = jsonify(discovery_template)

    resp.status_code = 200
    return resp
