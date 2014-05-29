#!/usr/bin/env python
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


import os


def main():
    config_folder = _create_config_folder()
    _create_config_file(config_folder)


def _create_config_folder():
    config_folder = os.path.join(os.path.expanduser('~'), '.gstack')
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)
    os.chmod(config_folder, 0o700)
    return config_folder


def _create_config_file(config_folder):
    config_file = open(config_folder + '/gstack.conf', 'w+')

    config_file.write('PATH = \'%s\'\n' % 'compute/v1/projects/')

    gstack_address = raw_input('gstack bind address [0.0.0.0]: ')
    if gstack_address == '':
        gstack_address = '0.0.0.0'
    config_file.write('GSTACK_BIND_ADDRESS = \'%s\'\n' % gstack_address)

    gstack_port = raw_input('gstack bind port [5000]: ')
    if gstack_port == '':
        gstack_port = '5000'
    config_file.write('GSTACK_PORT = \'%s\'\n' % gstack_port)

    cloudstack_host = raw_input('Cloudstack host [localhost]: ')
    if cloudstack_host == '':
        cloudstack_host = 'localhost'
    config_file.write('CLOUDSTACK_HOST = \'%s\'\n' % cloudstack_host)

    cloudstack_port = raw_input('Cloudstack port [8080]: ')
    if cloudstack_port == '':
        cloudstack_port = '8080'
    config_file.write('CLOUDSTACK_PORT = \'%s\'\n' % cloudstack_port)

    cloudstack_protocol = raw_input('Cloudstack protocol [http]: ')
    if cloudstack_protocol == '':
        cloudstack_protocol = 'http'
    config_file.write('CLOUDSTACK_PROTOCOL = \'%s\'\n' % cloudstack_protocol)

    cloudstack_path = raw_input('Cloudstack path [/client/api]: ')
    if cloudstack_path == '':
        cloudstack_path = '/client/api'
    config_file.write('CLOUDSTACK_PATH = \'%s\'\n' % cloudstack_path)

    config_file.close()
