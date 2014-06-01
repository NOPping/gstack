#!/usr/bin/env python
# encoding: utf-8

import mock

from gstack.helpers import read_file
from . import GStackAppTestCase

class ZonesTestCase(GStackAppTestCase):

    def test_list_images(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_images.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/images', headers=headers)

        self.assert_ok(response)

    def test_get_image(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_images.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/images/imagename', headers=headers)

        self.assert_ok(response)

    def test_get_zone_not_found(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/empty_describe_images.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/images/imagename', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/exampleproject/global/images/imagename\' was not found' \
                in response.data
