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

import json
from flask import request
from pyoauth2.provider import ResourceProvider
from gcecloudstack.models.accesstoken import AccessToken
from gcecloudstack.models.client import Client
from gcecloudstack.services.cloudstackResourceAuthorization import CloudstackResourceAuthorization


class CloudstackResourceProvider(ResourceProvider):

    @property
    def authorization_class(self):
        return CloudstackResourceAuthorization

    def get_authorization_header(self):
        return request.headers.get('Authorization')

    def validate_access_token(self, access_token, authorization):
        found_access_token = AccessToken.query.get(access_token)
        if found_access_token is not None:
            access_token_data = json.loads(found_access_token.data)
            client = Client.query.get(access_token_data.get('client_id'))

            authorization.is_valid = True
            authorization.client_id = access_token_data.get('client_id')
            authorization.expires_in = access_token_data.get('expires_in')
            authorization.jsessionid = client.jsessionid
            authorization.sessionkey = client.sessionkey

resource_provider = CloudstackResourceProvider()
