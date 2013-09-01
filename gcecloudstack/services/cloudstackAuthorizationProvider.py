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

from pyoauth2.provider import AuthorizationProvider
from gcecloudstack import app
import requester


class CloudstackAuthorizationProvider(AuthorizationProvider):

    def validate_client_id(self, client_id):
        return client_id is not None

    def validate_client_secret(self, client_id, client_secret):
        response = requester.make_request('listCapabilities', {}, None, app.config['HOST'], app.config['PORT'],
                                          client_id, client_secret, app.config['PROTOCOL'], app.config['PATH'])

        if 'HTTP Error 401: Unauthorized' in response :
            print 'Authorization unsuccessful: invalid api key / secret combination'
            return False
        return True


    def validate_redirect_uri(self, client_id, redirect_uri):
        return redirect_uri is not None

    def validate_access(self):
        return True

    def validate_scope(self, client_id, scope):
        return True

    def persist_authorization_code(self, client_id, code, scope):
        print 'persist authorization code'

    def persist_token_information(self, client_id, scope, access_token,
                          token_type, expires_in, refresh_token, data):
        print 'persist token information'

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
        print 'discarding authorization code'

    def discard_refresh_token(self, client_id, refresh_token):
        print 'discarding refresh token'

    def discard_client_user_tokens(self, client_id, user_id):
        print 'discard client token'
