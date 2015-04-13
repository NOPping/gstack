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


class MachineTypesTestCase(GStackAppTestCase):

    def test_list_machine_types(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_service_offerings.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/exampleproject/zones/examplezone/machineTypes', headers=headers)

        self.assert_ok(response)

    def test_aggregated_list_machine_types(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_service_offerings.json')
        get.return_value.status_code = 200

        get_zones = mock.Mock()
        get_zones.return_value = json.loads(
            read_file('tests/data/valid_describe_zone.json'))

        with mock.patch('requests.get', get):
            with mock.patch(
                'gstack.controllers.zones._get_zones',
                get_zones
            ):
                headers = {
                    'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
                response = self.get(
                    '/compute/v1/projects/projectid/aggregated/machineTypes', headers=headers)

        self.assert_ok(response)

    def test_list_machine_types_with_name_filter(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_service_offering.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/projectid/zones/zonename/machineTypes?filter=name+eq+machinetypename',
                headers=headers)

        self.assert_ok(response)

    def test_get_machine_type(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_service_offering.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/exampleproject/zones/examplezone/machineTypes/machinetypename', headers=headers)

        self.assert_ok(response)

    def test_get_machine_type_machine_type_not_found(self):

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_service_offering.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/exampleproject/zones/examplezone/machineTypes/invalidmachinetypename', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/exampleproject/zones/examplezone/machineTypes/invalidmachinetypename\' was not found' \
            in response.data
