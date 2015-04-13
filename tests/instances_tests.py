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
from gstack import publickey_storage

from gstack.helpers import read_file
from . import GStackAppTestCase


class InstancesTestCase(GStackAppTestCase):

    def test_list_instances(self):
        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_instances.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/exampleproject/zones/examplezone/instances', headers=headers)

        self.assert_ok(response)

    def test_aggregated_list_instances(self):
        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_instances.json')
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
                    '/compute/v1/projects/projectid/aggregated/instances', headers=headers)

        self.assert_ok(response)

    def test_list_instances_with_name_filter(self):
        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_instance.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/projectid/zones/zonename/instances?filter=name+eq+instancename',
                headers=headers)

        self.assert_ok(response)

    def test_aggregated_list_instances_with_name_filter(self):
        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_instance.json')
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
                    '/compute/v1/projects/projectid/aggregated/instances?filter=name+eq+instancename',
                    headers=headers)

        self.assert_ok(response)

    def test_get_instance(self):
        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_describe_instance.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/exampleproject/zones/examplezone/instances/instancename', headers=headers)

        self.assert_ok(response)

    def test_get_instance_instance_not_found(self):
        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/empty_describe_instances.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/exampleproject/zones/examplezone/instances/instancename', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/exampleproject/zones/examplezone/instances/instancename\' was not found' \
            in response.data

    def test_delete_instance(self):
        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_async_destroy_vm.json')
        get.return_value.status_code = 200

        get_instance = mock.Mock()
        get_instance.return_value = json.loads(
            read_file('tests/data/valid_get_instance.json'))

        get_async_result = mock.Mock()
        get_async_result.return_value = json.loads(
            read_file('tests/data/valid_run_instance.json'))

        publickey_storage['admin'] = 'testkey'

        with mock.patch('requests.get', get):
            with mock.patch(
                'gstack.controllers.get_item_with_name',
                get_instance
            ):
                with mock.patch(
                    'gstack.controllers.operations._get_async_result',
                    get_async_result
                ):
                    headers = {
                        'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
                    response = self.delete(
                        '/compute/v1/projects/admin/zones/examplezone/instances/instancename', headers=headers)

        self.assert_ok(response)

    def test_add_instance(self):
        data = {
            'kind':  'compte#instance',
            'machineType':  'https://localhost:5000/compte/v1/projects/brogand93@darrenbrogan.ie/zones/ch-gva-2/machineTypes/machinetypename',
            'description':  '',
            'tags': {
                'items': []
            },
            'disks': [{
                'deviceName':  'machinetypename',
                'initializeParams': {
                    'diskName':  'machinetypename',
                    'sourceImage':  'https://localhost:5000/compte/v1/projects/brogand93@darrenbrogan.ie/global/images/imagename'
                },
                'autoDelete': False,
                'boot': True,
                'mode':  'READ_WRITE',
                'type':  'PERSISTENT'
            }],
            'metadata': {
                'items': [],
                'kind':  'compte#metadata'
            },
            'networkInterfaces': [{
                'accessConfigs': [{
                    'type':  'ONE_TO_ONE_NAT',
                    'name':  'External NAT'
                }],
                'network':  'https://localhost:5000/compte/v1/projects/brogand93@darrenbrogan.ie/global/networks/networkname'
            }],
            'name':  'foobar'
        }

        publickey_storage['admin'] = 'testkey'

        data = json.dumps(data)

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_async_deploy_vm.json')
        get.return_value.status_code = 200

        get_templates = mock.Mock()
        get_templates.return_value = json.loads(
            read_file('tests/data/valid_get_image.json'))

        get_zones = mock.Mock()
        get_zones.return_value = json.loads(
            read_file('tests/data/valid_get_zone.json'))

        get_service_offerings = mock.Mock()
        get_service_offerings.return_value = json.loads(
            read_file('tests/data/valid_get_service_offering.json'))

        get_networks = mock.Mock()
        get_networks.return_value = json.loads(
            read_file('tests/data/valid_get_security_group.json'))

        get_async_result = mock.Mock()
        get_async_result.return_value = json.loads(
            read_file('tests/data/valid_run_instance.json'))

        with mock.patch('requests.get', get):
            with mock.patch(
                'gstack.controllers.images.get_template_by_name',
                get_templates
            ):
                with mock.patch(
                    'gstack.controllers.zones.get_zone_by_name',
                    get_zones
                ):
                    with mock.patch(
                            'gstack.controllers.machine_type.get_machinetype_by_name',
                            get_service_offerings
                    ):
                        with mock.patch(
                                'gstack.controllers.networks.get_network_by_name',
                                get_networks
                        ):
                            with mock.patch(
                                'gstack.controllers.operations._get_async_result',
                                get_async_result
                            ):
                                headers = {
                                    'authorization': 'Bearer ' + str(GStackAppTestCase.access_token),
                                }

                                response = self.post_json(
                                    '/compute/v1/projects/admin/zones/zonename/instances', data=data, headers=headers)

        self.assert_ok(response)
