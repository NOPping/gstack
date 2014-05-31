#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import mock

import json

from gstack import app, configure_app
from gstack.helpers import read_file
from . import settings
from .utils import FlaskTestCaseMixin

class GStackTestCase(TestCase):
    pass

class GStackAppTestCase(FlaskTestCaseMixin, GStackTestCase):

    access_token = ""

    def _configure_app(self):
        configure_app(settings=settings)

    def _auth_example_user(self):
        data = {}
        data['code'] = 'hjrZryvgLYo3R833NkHHV8jYmxQhsD8TjKWzOm2f'
        data['grant_type'] = 'authorization_code'
        data['client_id'] = 'ExampleAPIKey'
        data['client_secret'] = 'eXmaPlEm8XQwezvLOd10Qt3wXH7j9mRgaKbEg3nRDnj7FtlF3yx54EWd9mR5sB1ec5LQDV6gjpy6sfDo6ndUeeww'
        data['redirect_uri'] = 'http://localhost:8000'

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/list_capabilities.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            self.get('/oauth2/auth?scope=example&redirect_uri=http://127.0.0.1:9999&response_type=code&client_id=ExampleAPIKey&access_type=offline')
            response = self.post('/oauth2/token', data=data)

        GStackAppTestCase.access_token = json.loads(response.data)['access_token']

        self.assert_ok(response)



    def setUp(self):
        super(GStackTestCase, self).setUp()
        self._configure_app()
        self.app = app
        self.client = self.app.test_client()
        self._auth_example_user()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        super(GStackTestCase, self).tearDown()
        self.app_context.pop()

