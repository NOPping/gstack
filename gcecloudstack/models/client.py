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

from gcecloudstack import db


class Client(db.Model):
    client_id = db.Column(db.String(100), primary_key=True, unique=True)
    secret_key = db.Column(db.String(100), unique=True)
    access_key = db.Column(db.String(100), index=True, unique=True)
    refresh_key = db.Column(db.String(100), index=True, unique=True)

def __init__(self, client_id, secret_key, access_key, refresh_key):
    self.client_id = client_id
    self.secret_key = secret_key
    self.access_key = access_key
    self.refresh_key = refresh_key
