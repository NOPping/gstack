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

from unittest import TestCase

import mock
import json

from gstack import app, configure_app
from gstack.helpers import read_file
from . import settings
from gstack.core import db
from .utils import FlaskTestCaseMixin


class GStackTestCase(TestCase):
    pass


class GStackAppTestCase(FlaskTestCaseMixin, GStackTestCase):

    access_token = ""

    def _configure_app(self):
        configure_app(settings=settings)

    def _unauthed_user(self):
        response = self.get(
            '/compute/v1/projects/exampleproject/global/images')
        self.assert_unauthorized(response)

    def _auth_example_user(self):
        data = {}
        data['code'] = 'hjrZryvgLYo3R833NkHHV8jYmxQhsD8TjKWzOm2f'
        data['grant_type'] = 'authorization_code'
        data['client_id'] = 'ExampleAPIKey'
        data[
            'client_secret'] = 'eXmaPlEm8XQwezvLOd10Qt3wXH7j9mRgaKbEg3nRDnj7FtlF3yx54EWd9mR5sB1ec5LQDV6gjpy6sfDo6ndUeeww'
        data['redirect_uri'] = 'http://localhost:8000'

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/list_capabilities.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            self.get(
                '/oauth2/auth?scope=example&redirect_uri=http://127.0.0.1:9999&response_type=code&client_id=ExampleAPIKey&access_type=offline')
            response = self.post_html('/oauth2/token', data=data)

        GStackAppTestCase.access_token = json.loads(
            response.data)['access_token']

        self.assert_ok(response)

    def setUp(self):
        super(GStackTestCase, self).setUp()
        self._configure_app()
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self._unauthed_user()
        self._auth_example_user()

    def tearDown(self):
        super(GStackTestCase, self).tearDown()
        db.drop_all()
        self.app_context.pop()
