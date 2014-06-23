#!/usr/bin/env python
# encoding: utf-8

import mock

from gstack.helpers import read_file
from . import GStackAppTestCase

class OperationsTestCase(GStackAppTestCase):

    def test_query_operation(self):
        get = mock.Mock()
        get.return_value.text = read_file('tests/data/destroy_vm_async_pending.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/operations/exampleoperation', headers=headers)

        self.assert_ok(response)