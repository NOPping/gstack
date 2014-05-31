#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from gstack import app, configure_app
from . import settings
from .utils import FlaskTestCaseMixin

class GStackTestCase(TestCase):
    pass

class GStackAppTestCase(FlaskTestCaseMixin, GStackTestCase):

    def _configure_app(self):
        configure_app(settings=settings)

    def setUp(self):
        super(GStackTestCase, self).setUp()
        self._configure_app()
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        super(GStackTestCase, self).tearDown()
        self.app_context.pop()

