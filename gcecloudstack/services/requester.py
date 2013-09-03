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

try:
    import base64
    import hashlib
    import hmac
    import httplib
    import json
    import os
    import pdb
    import re
    import shlex
    import sys
    import time
    import types
    import urllib
    import urllib2
    import requests

except ImportError as e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()


def logger_debug(logger, message):
    if logger is not None:
        logger.debug(message)


def make_request(command, args, logger, host, port,
                 apikey, secretkey, protocol, path):
    response = None
    error = None

    if protocol != 'http' and protocol != 'https':
        error = "Protocol must be 'http' or 'https'"
        return None, error

    if args is None:
        args = {}

    args["command"] = command
    args["apiKey"] = apikey
    args["response"] = "json"
    request = zip(args.keys(), args.values())
    request.sort(key=lambda x: x[0].lower())

    request_url = "&".join(["=".join([r[0], urllib.quote_plus(str(r[1]))])
                           for r in request])
    hashStr = "&".join(["=".join([r[0].lower(),
                        str.lower(urllib.quote_plus(str(r[1])))
                                  .replace("+", "%20")]) for r in request])

    sig = urllib.quote_plus(base64.encodestring(hmac.new(secretkey, hashStr,
                            hashlib.sha1).digest()).strip())
    request_url += "&signature=%s" % sig
    request_url = "%s://%s:%s%s?%s" % (protocol, host, port, path, request_url)

    try:
        logger_debug(logger, "Request sent: %s" % request_url)
        connection = urllib2.urlopen(request_url)
        response = connection.read()
    except Exception as e:
        error = str(e)

    logger_debug(logger, "Response received: %s" % response)
    if error is not None:
        logger_debug(logger, error)

    return response, error


def encodeURIComponent(str):
    return urllib.quote(str, safe='~()*!.\'')

# If needed we can use something like the three functions below
# needs testing


def cloud_login(hostname, username, password, tmp_name):
    payload = {'command': 'login', 'username': username, 'password': password,
               'response': 'json'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}
    url = 'http://' + hostname + ':8080/client/api'
    response = json.loads(request.post(url=url, params=payload,
                          headers=headers, cookies=tmp_name))
    if response.get('errorresponse'):
        print response['errorresponse']['errortext']
        return None
    return response['loginresponse']


def get_keys(hostname, loginresp, tmp_name):
    payload = {'command': 'listUsers', 'id': loginresp['userid'],
               'sessionkey': encodeURIComponent(loginresp['sessionkey']),
               'response': 'json'}
    headers = {'Content-Type': 'application/json'}
    url = 'http://' + hostname + ':8080/client/api'
    response = json.loads(request.post(url=url, params=payload,
                                       headers=headers, cookies=tmp_name))
    logging.debug(response)
    user = response['listusersresponse']['user'][0]
    if not 'apikey' in user:
        return None
    return user['apikey'], user['secretkey']


def register_keys(hostname, loginresp, tmp_name):
    payload = {'command': 'registerUserKeys', 'id': loginresp['userid'],
               'sessionkey': encodeURIComponent(loginresp['sessionkey']),
               'response': 'json'}
    headers = {'Content-Type': 'application/json'}
    url = 'http://' + hostname + ':8080/client/api'
    response = json.loads(request.post(url=url, params=payload,
                                       headers=headers, cookies=tmp_name))
    logging.debug(response)
    return response


def get_api_key(hostname, username, password):
    tmp_cookie = tempfile.mkstemp(suffix=".cookie")
    tmp_name = tmp_cookie[1]
    loginresp = cloud_login(hostname, username, password, tmp_name)
    if not loginresp:
        return None

    keypair = get_keys(hostname, loginresp, tmp_name)

    if not keypair:
        response = registerKeys(hostname, loginresp, tmp_name)
        keys = response['registeruserkeysresponse']
        if 'userkeys' in keys:
            keypair = {'apikey': keys['userkeys']['apikey'],
                       'secretkey': keys['userkeys']['secretkey']}

    os.remove(tmp_name)
    return keypair
