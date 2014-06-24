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
import argparse

from alembic import command
from ConfigParser import SafeConfigParser
from alembic.config import Config as AlembicConfig


def main():
    config_folder = _create_config_folder()
    _create_config_file(config_folder)
    _create_database()


def _create_config_folder():
    config_folder = os.path.join(os.path.expanduser('~'), '.gstack')
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)
    os.chmod(config_folder, 0o700)
    return config_folder


def _create_config_file(config_folder):
    args = _generate_args()
    profile = args.pop('profile')
    config_file_path = config_folder + '/gstack.conf'
    config = _modify_config_profile(config_file_path, profile)
    config_file = open(config_file_path, 'w+')
    config.write(config_file)


def _generate_args():
    parser = argparse.ArgumentParser(
        'Command line utility for configuring gstack'
    )

    parser.add_argument(
        '-p',
        '--profile',
        required=False,
        help='The profile to run gstack with, default is initial',
        default='initial'
    )

    args = parser.parse_args()

    return vars(args)


def _modify_config_profile(config_file, profile):
    config = SafeConfigParser()
    config.read(config_file)

    if not config.has_section(profile):
        config.add_section(profile)

    config = _set_attribute_of_profile(
        config, profile, 'gstack_bind_address', 'gstack bind address', 'localhost'
    )
    config = _set_attribute_of_profile(
        config, profile, 'gstack_port', 'gstack bind port', '5000'
    )
    config = _set_attribute_of_profile(
        config, profile, 'cloudstack_host', 'Cloudstack host', 'localhost'
    )
    config = _set_attribute_of_profile(
        config, profile, 'cloudstack_port', 'Cloudstack port', '8080'
    )
    config = _set_attribute_of_profile(
        config, profile, 'cloudstack_protocol', 'Cloudstack protocol', 'http'
    )
    config = _set_attribute_of_profile(
        config, profile, 'cloudstack_path', 'Cloudstack path', '/client/api'
    )

    return config


def _set_attribute_of_profile(config, profile, attribute, message, default):
    if config.has_option(profile, attribute):
        default = config.get(profile, attribute)

    attribute_value = _read_in_config_attribute_or_use_default(message, default)

    config.set(profile, attribute, attribute_value)
    return config


def _read_in_config_attribute_or_use_default(message, default):
    attribute = raw_input(message + ' [' + default + ']: ')
    if attribute == '':
        attribute = default

    return attribute


def _create_database():
    directory = os.path.join(os.path.dirname(__file__), '../migrations')
    database_config = AlembicConfig(os.path.join(
        directory,
        'alembic.ini'
    ))
    database_config.set_main_option('script_location', directory)
    command.upgrade(database_config, 'head', sql=False, tag=None)
