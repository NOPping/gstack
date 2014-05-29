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

from gstack import app, configure_app

from OpenSSL import SSL


def main():
    configure_app()
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.use_privatekey_file(app.config['DATA'] + '/server.key')
    context.use_certificate_file(app.config['DATA'] + '/server.crt')

    app.run(
        host=app.config['GSTACK_BIND_ADDRESS'],
        port=int(app.config['GSTACK_PORT']),
        debug=app.config['DEBUG'],
        ssl_context=context
    )

if __name__ == '__main__':
    main()
