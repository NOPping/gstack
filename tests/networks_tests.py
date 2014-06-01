#!/usr/bin/env python
# encoding: utf-8

import mock

from gstack.helpers import read_file
from . import GStackAppTestCase

class NetworksTestCase(GStackAppTestCase):

    def test_list_networks(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_security_groups.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/networks', headers=headers)

        self.assert_ok(response)

    def test_get_network(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_security_group.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/networks/networkname', headers=headers)

        self.assert_ok(response)

    def test_get_network_network_not_found(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/empty_describe_security_groups.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/networks/networkname', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/exampleproject/global/networks/networkname\'' \
                in response.data
