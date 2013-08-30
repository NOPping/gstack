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
        """ Can we call to Cloudstack to check if a client id exists """
        return client_id is not None

    def validate_client_secret(self, client_id, client_secret):
        """ Can we call to Cloudstack to see if their secret key exists
            A messy implementation of this would be to just call any user
            api command and check that it gives a successful response
        """
        
        """ Hostname currently set to ianduffy.ie for testing purposes"""
        hostname = 'ianduffy.ie'
        response = requester.make_request('listCapabilities', {}, None, hostname, app.config['PORT'],
                                          client_id, client_secret, app.config['PROTOCOL'], app.config['PATH'])
        
        if 'HTTP Error 401: Unauthorized' in response :
            print 'Authorization unsuccessful: invalid api key / secret combination'
            return False
        return True
        

    def validate_redirect_uri(self, client_id, redirect_uri):
        """ Ensure the app knows the redirect_uri """
        return redirect_uri is not None

    def validate_access(self):
        """ Related to validation of OAuth token generation
            Not sure if important for our purposes
        """
        return True

    def validate_scope(self, client_id, scope):
        """ I see no issues in leaving this as true. We do not know what
            scope(s) GCE may use. User will be restricted access by their
            CS client key and secret anyways
        """
        return True

    def persist_authorization_code(self, client_id, code, scope):
        """ Store code with expiry """
        print 'persist authorization code'

    def persist_token_information(self, client_id, scope, access_token, 
                          token_type, expires_in, refresh_token, data):
        """ Store all token information """
        print 'persist token information'

    def from_authorization_code(self, client_id, code, scope):
        """ Return stored auth code """
        return {
            'client_id': client_id,
            'code': code,
            'scope': scope,
        }

    def from_refresh_token(self, client_id, refresh_token, scope):
        """ return stored refresh token """
        return {
            'client_id': client_id,
            'refresh_token': refresh_token,
            'scope': scope,
        }

    def discard_authorization_code(self, client_id, code):
        """ Remove auth code """
        key = 'oauth2.authorization_code.%s:%s' % (client_id, code) 
        self.redis.delete(key)

    def discard_refresh_token(self, client_id, refresh_token):
        """ Remove auth token """
        print 'discarding refresh token'

    def discard_client_user_tokens(self, client_id, user_id):
        """ remove client tokens """
        """ seems like were going to need this regardless of what way we 
            implement OAuth access tokens so I included it"""
        
        keys = 'oauth2.client_user.%s:%s' % (client_id, user_id) 
        pipe = self.redis.pipeline() 
        for key in self.redis.smembers(keys): 
            pipe.delete(key) 
            pipe.execute() 
