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

from pyoauth2.provider import ResourceAuthorization
from pyoauth2.provider import ResourceProvider
from pyoauth2.provider import AuthorizationProvider


from gstack import db
from gstack.services import requester
from gstack.models.client import Client
from gstack.models.accesstoken import AccessToken
from gstack.models.refreshtoken import RefreshToken


class CloudstackAuthorizationProvider(AuthorizationProvider):

    def validate_client_id(self, client_id):
        return client_id is not None

    def validate_client_secret(self, client_id, client_secret):
        command = 'listCapabilities'
        args = {}
        cloudstack_response = requester.make_request(
            command,
            args,
            client_id,
            client_secret
        )

        if cloudstack_response:
            existing_client = Client.query.get(client_id)

            if existing_client is not None:
                existing_client.client_secret = client_secret
            else:
                client = Client(
                    client_id=client_id,
                    client_secret=client_secret
                )
                db.session.add(client)

            db.session.commit()
            return True
        else:
            return False

    def validate_redirect_uri(self, client_id, redirect_uri):
        return True

    def validate_access(self):
        return True

    def validate_scope(self, client_id, scope):
        return True

    def persist_authorization_code(self, client_id, code, scope):
        return

    def persist_token_information(
            self,
            client_id,
            scope,
            access_token,
            token_type,
            expires_in,
            refresh_token,
            data):
        client = Client.query.get(client_id)
        if client is not None:
            existing_access_token = AccessToken.query.filter_by(
                client_id=client_id).first()
            existing_refresh_token = RefreshToken.query.filter_by(
                client_id=client_id).first()

            if existing_access_token is not None:
                existing_access_token.access_token = access_token
                existing_access_token.data = json.dumps(data)
                existing_access_token.expires_in = expires_in
            else:
                db.session.add(
                    AccessToken(
                        access_token=access_token, client_id=client_id,
                        expires_in=expires_in, data=json.dumps(data)
                    )
                )

            if existing_refresh_token is not None:
                existing_refresh_token.refresh_token = refresh_token
                existing_refresh_token.data = json.dumps(data)
            else:
                db.session.add(
                    RefreshToken(
                        refresh_token=refresh_token, client_id=client_id,
                        data=json.dumps(data)
                    )
                )

            db.session.commit()
            return True
        else:
            return False

    def from_authorization_code(self, client_id, code, scope):
        return {
            'client_id': client_id,
            'code': code,
            'scope': scope,
        }

    def from_refresh_token(self, client_id, refresh_token, scope):
        found_refresh_token = RefreshToken.query.get(refresh_token)
        if found_refresh_token is not None and found_refresh_token.data != 'false':
            data = json.loads(found_refresh_token.data)
            if (scope == '' or scope == data.get('scope')) and client_id == data.get('client_id'):
                return data
        else:
            return False

    def discard_authorization_code(self, client_id, code):
        return None

    def discard_refresh_token(self, client_id, refresh_token):
        found_refresh_token = RefreshToken.query.get(refresh_token)
        if found_refresh_token is not None:
            db.session.delete(found_refresh_token)
            db.session.commit()


class CloudstackResourceAuthorization(ResourceAuthorization):
    client_secret = None


class CloudstackResourceProvider(ResourceProvider):

    @property
    def authorization_class(self):
        return CloudstackResourceAuthorization

    def get_authorization_header(self):
        return request.headers.get('Authorization')

    def validate_access_token(self, access_token, authorization):
        found_access_token = AccessToken.query.get(access_token)
        if found_access_token is not None and found_access_token.data != 'false':
            access_token_data = json.loads(found_access_token.data)
            client = Client.query.get(access_token_data.get('client_id'))

            authorization.is_valid = True
            authorization.client_id = access_token_data.get('client_id')
            authorization.expires_in = access_token_data.get('expires_in')
            authorization.client_secret = client.client_secret
