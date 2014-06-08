#!/usr/bin/env python
# encoding: utf-8

import mock
import json

from gstack.helpers import read_file
from . import GStackAppTestCase

class FirewallsTestCase(GStackAppTestCase):

    def test_list_firewalls(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_security_groups.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/firewalls', headers=headers)

        self.assert_ok(response)


    def test_get_firewall(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_describe_security_group.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/firewalls/securitygroupname', headers=headers)

        self.assert_ok(response)

    def test_get_firewall_firewall_not_found(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/empty_describe_security_groups.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
            response = self.get('/compute/v1/projects/exampleproject/global/firewalls/securitygroupname', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/exampleproject/global/firewalls/securitygroupname\' was not found' \
                in response.data

    def test_add_firewall(self):
        data = {
            "kind": "compute#firewall",
            "network": "https://localhost:5000/compute/v1/projects/brogand93@darrenbrogan.ie/global/networks/default",
            "description": "",
            "sourceRanges": ["0.0.0.0/0"],
            "allowed": [{
                "IPProtocol": "6",
                "ports": ["22"]
            }],
            "name": "ssh"
        }

        data = json.dumps(data)

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_create_security_group.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
             headers = {
                 'authorization': 'Bearer ' + str(GStackAppTestCase.access_token),
             }

             response = self.post_json('/compute/v1/projects/exampleproject/global/firewalls', data=data, headers=headers)

        self.assert_ok(response)

    def test_delete_firewall(self):

        get = mock.Mock()
        get.return_value.text = read_file('tests/data/valid_delete_security_group.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
             headers = {
                 'authorization': 'Bearer ' + str(GStackAppTestCase.access_token),
             }

             response = self.delete('/compute/v1/projects/exampleproject/global/firewalls/firewallname', headers=headers)

        self.assert_ok(response)
