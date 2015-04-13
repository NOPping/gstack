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
import mock
import json

from gstack.helpers import read_file
from . import GStackAppTestCase


class NetworksTestCase(GStackAppTestCase):

    def test_list_networks(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_security_groups.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/exampleproject/global/networks', headers=headers)

        self.assert_ok(response)

    def test_get_network(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_security_group.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/exampleproject/global/networks/networkname', headers=headers)

        self.assert_ok(response)

    def test_get_network_network_not_found(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/empty_describe_security_groups.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/exampleproject/global/networks/networkname', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/exampleproject/global/networks/networkname\'' \
            in response.data

    def test_add_network(self):
        data = {
            'IPv4Range': '10.0.0.0/8',
            'kind': 'compute#network',
            'name': 'networkname',
            'description': ''
        }

        data = json.dumps(data)

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_create_security_group.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token),
            }

            response = self.post_json(
                '/compute/v1/projects/admin/global/networks', data=data, headers=headers)

        self.assert_ok(response)

    def test_add_network_network_duplicate(self):
        data = {
            'IPv4Range': '10.0.0.0/8',
            'kind': 'compute#network',
            'name': 'networkname',
            'description': ''
        }

        data = json.dumps(data)

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/duplicate_create_security_group.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token),
            }

            response = self.post_json(
                '/compute/v1/projects/admin/global/networks', data=data, headers=headers)

        assert 'RESOURCE_ALREADY_EXISTS' in response.data

    def test_delete_network(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_delete_security_group.json')
        get.return_value.status_code = 200

        get_networks = mock.Mock()
        get_networks.return_value = json.loads(
            read_file('tests/data/valid_get_security_group.json'))

        with mock.patch('requests.get', get):
            with mock.patch('gstack.controllers.get_item_with_name', get_networks):
                headers = {
                    'authorization': 'Bearer ' + str(GStackAppTestCase.access_token),
                }

                response = self.delete(
                    '/compute/v1/projects/exampleproject/global/networks/networkname', headers=headers)

        self.assert_ok(response)

    def test_delete_network_network_not_found(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_delete_security_group.json')
        get.return_value.status_code = 200

        get_networks = mock.Mock()
        get_networks.return_value = None

        with mock.patch('requests.get', get):
            with mock.patch('gstack.controllers.get_item_with_name', get_networks):
                headers = {
                    'authorization': 'Bearer ' + str(GStackAppTestCase.access_token),
                }

                response = self.delete(
                    '/compute/v1/projects/exampleproject/global/networks/invalidnetworkname', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/exampleproject/global/networks/invalidnetworkname\'' \
            in response.data
