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

from gcecloudstack.models.client import Client
from gcecloudstack.models.accessKey import AccessKey
from gcecloudstack.models.refreshKey import RefreshKey
from pyoauth2.provider import AuthorizationProvider
from gcecloudstack import app, db
from . import requester
import json


class CloudstackAuthorizationProvider(AuthorizationProvider):

    def validate_client_id(self, username):
        return username is not None

    def validate_client_secret(self, username, password):
        response = requester.cloud_login(username, password)
        if response:
            jsessionid = response.cookies['JSESSIONID']

            data = json.loads(response.text)
            sessionkey = data['loginresponse']['sessionkey']

            client = Client(username=username,jsessionid=jsessionid,sessionkey=sessionkey)
            db.session.add(client)
            db.session.commit()
        else:
            print "empty"
            return False

    def validate_redirect_uri(self, client_id, redirect_uri):
        return True

    def validate_access(self):
        return True

    def validate_scope(self, client_id, scope):
        return True

    def persist_authorization_code(self, client_id, code, scope):
        print 'persist  authorization code'

    def persist_token_information(self, client_id, scope, access_token,
                                  token_type, expires_in,
                                  refresh_token, data):
        print client_id
        print access_token
        print refresh_token
        print data

    def from_authorization_code(self, client_id, code, scope):
        return {
            'client_id': client_id,
            'code': code,
            'scope': scope,
        }

    def from_refresh_token(self, client_id, refresh_token, scope):
        return {
            'client_id': client_id,
            'refresh_token': refresh_token,
            'scope': scope,
        }

    def discard_authorization_code(self, client_id, code):
        print "remove"

    def discard_refresh_token(self, client_id, refresh_token):
        print "remove"

    def discard_client_user_tokens(self, client_id, user_id):
        print "remove"
