#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import json
import re
import datetime

from json import dumps
from bson import json_util

import tornado.web

from wight.api.handlers.base import BaseHandler
from wight.models import LoadTest

URL_RE = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class LoadTestHandler(BaseHandler):

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    @BaseHandler.team_member
    def post(self, team, project_name):
        base_url = self.get_argument("base_url").strip()

        if not base_url or not URL_RE.match(base_url):
            self.set_status(400)
            self.finish()
            return

        project = [project for project in team.projects if project.name.lower().strip() == project_name.lower().strip()] or None
        if not project:
            self.set_status(404)
            self.finish()
            return

        project = project[0]

        test = LoadTest(status="Scheduled", base_url=base_url, team=team, created_by=self.current_user, project_name=project.name)
        test.save()

        self.set_status(200)
        self.write("OK")
        self.finish()

    @tornado.web.asynchronous
    @BaseHandler.authenticated
    @BaseHandler.team_member
    def get(self, team, project_name):
        quantity = self.get_argument("quantity").strip()
        quantity = int(quantity) if quantity else 20
        load_tests = LoadTest.get_sliced_by_team_and_project_name(team, project_name, quantity)
        self.set_status(200)
        response = dumps([load_test.to_dict() for load_test in load_tests])
        self.write(response)
        self.finish()