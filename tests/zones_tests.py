#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import mock

from gstack.helpers import read_file
from . import GStackAppTestCase

class ZonesTestCase(GStackAppTestCase):

    def test_list_zones(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/zones_search.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            print headers
            response = self.get('/compute/v1/projects/exampleproject/zones', headers=headers)

        self.assert_ok(response)
