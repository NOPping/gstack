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


class FlaskTestCaseMixin(object):

    @staticmethod
    def _html_data(kwargs):
        if not kwargs.get('content_type'):
            kwargs['content_type'] = 'application/x-www-form-urlencoded'
        return kwargs

    @staticmethod
    def _json_data(kwargs):
        if not kwargs.get('content_type'):
            kwargs['content_type'] = 'application/json'
        return kwargs

    @staticmethod
    def _request(method, *args, **kwargs):
        return method(*args, **kwargs)

    def post_html(self, *args, **kwargs):
        return (
            self._request(self.client.post, *args, **self._html_data(kwargs))
        )

    def post_json(self, *args, **kwargs):
        return (
            self._request(self.client.post, *args, **self._json_data(kwargs))
        )

    def get(self, *args, **kwargs):
        return self._request(self.client.get, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request(self.client.delete, *args, **kwargs)

    def assert_status_code(self, response, status_code):
        self.assertEquals(status_code, response.status_code)
        return response

    def assert_ok(self, response):
        return self.assert_status_code(response, 200)

    def assert_bad_request(self, response):
        return self.assert_status_code(response, 400)

    def assert_not_found(self, response):
        return self.assert_status_code(response, 404)

    def assert_unauthorized(self, response):
        return self.assert_status_code(response, 401)
