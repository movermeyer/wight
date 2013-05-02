#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from os.path import dirname, abspath, join
import socket

from mock import Mock
from tornado.netutil import bind_sockets
from tornado.testing import AsyncHTTPTestCase, get_unused_port, AsyncTestCase
from cement.utils import test

from wight.api.app import WightApp
from wight.api.config import Config

ROOT_PATH = abspath(join(dirname(__file__), '..'))


class TestCase(test.CementTestCase):
    def make_controller(self, cls, app=None, *args, **kw):
        if app is None:
            app = self.make_app(argv=args)
            app.setup()

        pargs = Mock(**kw)
        controller = cls(pargs=pargs)
        controller.app = app
        controller.log = Mock()

        return controller

    def fixture_for(self, filename):
        return join(ROOT_PATH, 'tests', 'fixtures', filename)


class ApiTestCase(AsyncHTTPTestCase):

    def setUp(self):
        AsyncTestCase.setUp(self)
        port = get_unused_port()
        sock = bind_sockets(port, 'localhost', socket.AF_INET)[0]
        self.__port = port
        setattr(self, "_AsyncHTTPTestCase__port", port)
        self.http_client = self.get_http_client()
        self._app = self.get_app()
        self.http_server = self.get_http_server()
        self.http_server.add_sockets([sock])

    def make_app(self, config=None):
        if not config:
            config = Config()
        return WightApp(config=config)
