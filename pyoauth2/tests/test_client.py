#!/usr/bin/env python
# encoding: utf-8
#
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.
#

from __future__ import absolute_import
import unittest
from pyoauth2.client import Client
from pyoauth2 import utils


class ClientTest(unittest.TestCase):

    def setUp(self):

        self.client = Client(
            client_id='some.client',
            client_secret='ASDFGHJKL',
            redirect_uri='https://example.com/pyoauth2redirect',
            authorization_uri='https://grapheffect.com/pyoauth2/auth',
            token_uri='https://grapheffect.com/pyoauth2/token')

    def test_get_authorization_code_uri(self):
        """Test client generation of authorization code uri."""
        uri = self.client.get_authorization_code_uri(state="app.state")

        # Check URI
        self.assertTrue(
            uri.startswith('https://grapheffect.com/pyoauth2/auth?'))

        # Check params
        params = utils.url_query_params(uri)
        self.assertEquals('code', params['response_type'])
        self.assertEquals('some.client', params['client_id'])
        self.assertEquals(
            'https://example.com/pyoauth2redirect', params['redirect_uri'])
        self.assertEquals('app.state', params['state'])
