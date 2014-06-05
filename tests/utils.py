#!/usr/bin/env python
# encoding: utf-8
"""
    tests.utils
    ~~~~~~~~~~~

    test utilities
"""


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

