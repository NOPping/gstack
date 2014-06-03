#!/usr/bin/env python
# encoding: utf-8

import mock

from gstack.helpers import read_file
from . import GStackAppTestCase

class RegionsTestCase(GStackAppTestCase):

    def test_list_regions(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_regions.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/regions', headers=headers)

        self.assert_ok(response)


    def test_get_region(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_regions.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/regions/regionname', headers=headers)

        self.assert_ok(response)

    def test_get_region_region_not_found(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_regions.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/regions/invalidregionname', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/exampleproject/regions/invalidregionname\' was not found' \
                in response.data

