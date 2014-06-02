#!/usr/bin/env python
# encoding: utf-8

import mock
import json

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

    def test_aggregated_list_instances_with_name_filter(self):

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
