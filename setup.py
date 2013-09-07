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

try:
    from setuptools import setup, find_packages
except ImportError:
    try:
        from distribute_setup import use_setuptools
        use_setuptools()
        from setuptools import setup, find_packages
    except ImportError:
        raise RuntimeError(
            "python setuptools is required to build gcecloudstack")

VERSION = '0.0.1'

import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()

setup(name="gcecloudstack",
      version=VERSION,
      description="Web Server exposing a GCE interface to Apache CloudStack",
      author="Ian Duffy, Darren Brogan, Sebastien Goasguen",
      author_email="",
      long_description="Google Compute Engine Interface to the Apache CloudStack API",
      platforms=("Any",),
      license="LICENSE.txt",
      package_data={'': ['LICENSE.txt', 'server.crt', 'server.key', 'app.db']},
      packages = [
          "gcecloudstack", "gcecloudstack.controllers", "gcecloudstack.models",
          "gcecloudstack.services", "pyoauth2"],
      install_requires=[
          "flask",
          "requests==0.14",
          "pyopenssl",
          "Flask-SQLAlchemy",
      ],
      zip_safe=False,
      entry_points="""
      [console_scripts]
      gcecloudstack = gcecloudstack.appserver:main
      """,
      )
