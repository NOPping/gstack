#!/usr/bin/env python
# encoding: utf-8

from . import GStackAppTestCase

class DiscoveryTestCase(GStackAppTestCase):

    def test_discovery(self):
        response = self.get('/discovery/v1/apis/compute/v1/rest')

        self.assert_ok(response)