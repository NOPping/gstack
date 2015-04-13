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

from __future__ import absolute_import
import unittest
from pyoauth2 import utils


class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://www.grapheffect.com/some/path;hello?c=30&b=2&a=10'

    def test_random_ascii_string(self):
        """Test that random_ascii_string generates string of correct length."""
        code = utils.random_ascii_string(25)

        self.assertEquals(25, len(code))

    def test_url_query_params(self):
        """Test get query parameters dict."""
        result = utils.url_query_params(self.base_url)

        self.assertEquals(result, {'c': '30', 'b': '2', 'a': '10'})

    def test_url_dequery(self):
        """Test url dequery removes query portion of URL."""
        result = utils.url_dequery(self.base_url)

        self.assertEquals(
            result, 'https://www.grapheffect.com/some/path;hello')

    def test_build_url(self):
        """Test that build_url properly adds query parameters."""
        result = utils.build_url(self.base_url, {'b': 20})

        # Note param ordering and correct new value for b
        self.assertEquals(
            result,
            'https://www.grapheffect.com/some/path;hello?a=10&c=30&b=20')
