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
from urllib2 import urlopen
from gcecloudstack import app
from . import requester


class CloudstackAuthorizationProvider(AuthorizationProvider):

    def validate_client_id(self, client_id):
        return client_id is not None

    def validate_client_secret(self, client_id, client_secret):
        response = requester.make_request(
            'listCapabilities', {}, None, app.config['HOST'],
            app.config['PORT'], client_id, client_secret,
            app.config['PROTOCOL'], app.config['PATH']
        )

        if 'HTTP Error 401: Unauthorized' in response:
            print 'Authorization unsuccessful: invalid api key / secret combination'
            return False
        return True

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

        access_key = 'ouath2.access_token.%s' % access_token
        user_access_key = AccessKey(access_key, expires_in)

        refresh_key = 'ouath2.refresh_token.%s:%s' % (client_id, refresh_token)
        refresh_token = RefreshKey(refresh_key, data)

        client_token = Client(
            client_id,
            data.get('code'),
            authorization_code,
            refresh_token
        )

        db.session.add(user_access_key)
        db.session.add(refresh_token)
        db.session.add(client_token)
        db.session.commit()

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
        access_key = 'ouath2.authorization_code.%s:%s' % (client_id, code)
        access_key_to_be_deleted = AccessKey.query.filter_by(access_key).all()
        if(access_key_to_be_deleted is not None):
            db.session.delete(access_key_to_be_deleted)
            db.session.commit()

    def discard_refresh_token(self, client_id, refresh_token):
        ref_key = 'ouath2.refresh_token.%s:%s' % (client_id, refresh_token)
        ref_key_to_be_deleted = RefreshKey.query.filter_by(ref_key).all()
        if(ref_key_to_be_deleted is not None):
            db.session.delete(ref_key_to_be_deleted)
            db.session.commit()

    def discard_client_user_tokens(self, client_id, user_id):
        client_to_be_deleted = Client.query.filter_by(client_id).all()
        if(client_to_be_deleted is not None):
            db.session.delete(client_to_be_deleted)
            db.session.commit()
