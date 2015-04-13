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


class ProjectsTestCase(GStackAppTestCase):

    def test_get_project(self):
        get = mock.Mock()
        get.return_value = json.loads(
            read_file('tests/data/valid_get_account.json'))

        get_tags = mock.Mock()
        get_tags.return_value.text = read_file(
            'tests/data/valid_describe_tags.json')
        get_tags.return_value.status_code = 200

        with mock.patch('requests.get', get_tags):
            with(mock.patch('gstack.controllers.get_item_with_name', get)):
                headers = {
                    'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
                response = self.get(
                    '/compute/v1/projects/accountname', headers=headers)

        self.assert_ok(response)

    def test_get_project_project_not_found(self):
        get = mock.Mock()
        get.return_value = json.loads(
            read_file('tests/data/valid_describe_account.json'))

        get_tags = mock.Mock()
        get_tags.return_value.text = read_file(
            'tests/data/valid_describe_tags.json')
        get_tags.return_value.status_code = 200

        with mock.patch('requests.get', get_tags):
            with(mock.patch('gstack.controllers._get_items', get)):
                headers = {
                    'authorization': 'Bearer ' + str(GStackAppTestCase.access_token)}
                response = self.get(
                    '/compute/v1/projects/invalidaccountname', headers=headers)

        self.assert_not_found(response)
        assert 'The resource \'/compute/v1/projects/invalidaccountname\' was not found' \
            in response.data

    def test_set_metadata(self):
        data = {
            'items': [{
                'key': 'sshKeys',
                'value': 'root:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDqQuui+xCVPXaFD4cP2MuWnDlktp9vMT/SNzF17UiAzKEbxT\
                                        /mPayTDArDbY/BgGYC5bHuGlb/eE1r4EGpwSXZitGkTI4ThldrSp0Em7psO8AibdpYuFxlOmDFp9wK\
                                        VD6xbY2HT1ySwvKi+ZwSR5yHcEKq15eV4eez/3qC1vIcssKmwu5+ZBneZAvWAfxHEKsQU0dsCVvHdn8\
                                        g7tFXXtg4QCGtE4yzK5v3/+f1AdtIi4hvJoMyi8MV0KSa8e/ravdHbgj44PncFBB8O6epVdXPbClZwt\
                                        kz9D6GEQaOArxk9tX8YEgTFnmsnNuaoZgs7giMj2N7jQe2qXh5R0nsTTuH brogand@microvac'
            }],
            'kind': 'compute#metadata'
        }

        data = json.dumps(data)

        get = mock.Mock()
        get.return_value.text = read_file(
            'tests/data/valid_register_keypair.json')
        get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            headers = {
                'authorization': 'Bearer ' + str(GStackAppTestCase.access_token),
            }

            response = self.post_json(
                '/compute/v1/projects/admin/setCommonInstanceMetadata', data=data, headers=headers)

        self.assert_ok(response)
