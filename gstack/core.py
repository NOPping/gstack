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

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Service(object):
    __model__ = None

    def _isinstance(self, model, raise_error=True):
        valid_type = isinstance(model, self.__model__)
        if not valid_type and raise_error:
            raise ValueError('%s is not of type %s' % (model, self.__model__))
        return valid_type

    def save(self, model):
        self._isinstance(model)
        db.session.add(model)
        db.session.commit()
        return model

    def get(self, primarykey):
        return self.__model__.query.get(primarykey)

    def create(self, **kwargs):
        return self.save(self.__model__(**kwargs))

    def delete(self, model):
        self._isinstance(model)
        db.session.delete(model)
        db.session.commit()
