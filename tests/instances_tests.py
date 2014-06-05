#!/usr/bin/env python
# encoding: utf-8

import mock
import json
from gstack import publickey_storage

from gstack.helpers import read_file
from . import GStackAppTestCase

class InstancesTestCase(GStackAppTestCase):

    def test_list_instances(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_instances.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/zones/examplezone/instances', headers=headers)

        self.assert_ok(response)

    def test_aggregated_list_instances(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_instances.json')
        get.return_value.status_code = 200

        get_zones = mock.Mock()
        get_zones.return_value = json.loads(read_file('tests/data/valid_describe_zone.json'))

        with mock.patch('requests.get', get):
            with mock.patch(
                'gstack.controllers.zones._get_zones',
                get_zones
            ):
                headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
                response = self.get('/compute/v1/projects/projectid/aggregated/instances', headers=headers)

        self.assert_ok(response)

    def test_list_instances_with_name_filter(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_instance.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get(
                '/compute/v1/projects/projectid/zones/zonename/instances?filter=name+eq+instancename',
                headers=headers)

        self.assert_ok(response)

    def test_aggregated_list_instances_with_name_filter(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_instance.json')
        get.return_value.status_code = 200

        get_zones = mock.Mock()
        get_zones.return_value = json.loads(read_file('tests/data/valid_describe_zone.json'))

        with mock.patch('requests.get', get):
            with mock.patch(
                'gstack.controllers.zones._get_zones',
                get_zones
            ):
                headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
                response = self.get(
                    '/compute/v1/projects/projectid/aggregated/instances?filter=name+eq+instancename',
                    headers=headers)

        self.assert_ok(response)

    def test_get_instance(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_instance.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/zones/examplezone/instances/instancename', headers=headers)

        self.assert_ok(response)

    def test_get_instance_instance_not_found(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/empty_describe_instances.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/zones/examplezone/instances/instancename', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/exampleproject/zones/examplezone/instances/instancename\' was not found' \
                in response.data

    def test_delete_instance(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_async_destroy_vm.json')
        get.return_value.status_code = 200

        get_instance_id = mock.Mock()
        get_instance_id.return_value = {'id':'virtualmachineid'}

        get_async_result = mock.Mock()
        get_async_result.return_value = json.loads(read_file('tests/data/valid_run_instance.json'))

        publickey_storage['admin'] = 'testkey'

        with mock.patch('requests.get', get):
            with mock.patch(
                    'gstack.controllers.instances._get_virtual_machine_by_name',
                    get_instance_id
                ):
                with mock.patch(
                    'gstack.controllers.operations._get_async_result',
                    get_async_result
                ):
                    headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
                    response = self.delete('/compute/v1/projects/admin/zones/examplezone/instances/instancename', headers=headers)

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
        get.return_value.text = read_file('tests/data/valid_async_deploy_vm.json')
        get.return_value.status_code = 200

        get_templates = mock.Mock()
        get_templates.return_value = json.loads(read_file('tests/data/valid_describe_images.json'))

        get_zones = mock.Mock()
        get_zones.return_value = json.loads(read_file('tests/data/valid_describe_zone.json'))

        get_service_offerings = mock.Mock()
        get_service_offerings.return_value = json.loads(read_file('tests/data/valid_describe_service_offering.json'))

        get_networks = mock.Mock()
        get_networks.return_value = json.loads(read_file('tests/data/valid_describe_security_group.json'))

        get_async_result = mock.Mock()
        get_async_result.return_value = json.loads(read_file('tests/data/valid_run_instance.json'))

        with mock.patch('requests.get', get):
            with mock.patch(
                'gstack.controllers.images._get_templates',
                get_templates
            ):
                with mock.patch(
                    'gstack.controllers.zones._get_zones',
                    get_zones
                ):
                     with mock.patch(
                        'gstack.controllers.machine_type._get_machinetypes',
                        get_service_offerings
                    ):
                         with mock.patch(
                            'gstack.controllers.networks._get_networks',
                            get_networks
                        ):
                            with mock.patch(
                                'gstack.controllers.operations._get_async_result',
                                get_async_result
                            ):
                                headers = {
                                    'authorization': 'Bearer ' + str(GStackAppTestCase.access_token),
                                }

                                response = self.post_json('/compute/v1/projects/admin/zones/zonename/instances', data=data, headers=headers)

        self.assert_ok(response)
