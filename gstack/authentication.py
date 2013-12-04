#!/usr/bin/env python
# encoding: utf-8
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

from flask import abort
from functools import wraps
from gstack.oauth2provider import CloudstackResourceProvider

resource_provider = CloudstackResourceProvider()


def required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization = resource_provider.get_authorization()
        if not authorization.is_valid:
            return abort(401)

        return f(authorization=authorization, *args, **kwargs)
    return decorated
