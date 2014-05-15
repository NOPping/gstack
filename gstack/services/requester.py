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
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import hashlib
import hmac
import base64
import urllib
import requests
import json
from flask import abort
from gstack import app


def make_request(command, args, client_id, client_secret):
    args['command'] = command
    args['apiKey'] = client_id
    args['response'] = 'json'

    request = zip(args.keys(), args.values())
    request.sort(key=lambda x: x[0].lower())

    request_url = "&".join(
        ["=".join([r[0], urllib.quote_plus(str(r[1]))]) for r in request])

    hashStr = "&".join(["=".join([r[0].lower(),
                                  str.lower(urllib.quote_plus(str(r[1]))).replace("+",
                                                                                  "%20")]) for r in request])

    sig = urllib.quote_plus(
        base64.encodestring(
            hmac.new(
                client_secret,
                hashStr,
                hashlib.sha1).digest()).strip())

    request_url += "&signature=%s" % sig

    request_url = "%s://%s:%s%s?%s" % (
        app.config['CLOUDSTACK_PROTOCOL'],
        app.config['CLOUDSTACK_HOST'],
        app.config['CLOUDSTACK_PORT'],
        app.config['CLOUDSTACK_PATH'],
        request_url
    )

    response = requests.get(request_url)

    cloudstack_response = json.loads(response.text)

    app.logger.debug(
        'status code: ' + str(response.status_code) +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    if response.status_code is 500:
        abort(response.status_code)
    else:
        return cloudstack_response
