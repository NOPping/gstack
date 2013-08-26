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
                       str.lower(urllib.quote_plus(str(r[1]))).replace("+",
                                                                       "%20")]) for r in request])

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
# needs to be re-written with request module

def cloudLogin(hostname, username, password, tmp_name):
    login = ("command=login&username=" + username + "&password=" + password +
             "&response=json")
    cmd = ['curl',
           '-H', 'Content-Type: application/x-www-form-urlencoded',
           '-H', 'Accept: application/json',
           '-X', 'POST',
           '-d', login,
           '-c', tmp_name,
           'http://' + hostname + ':8080/client/api']
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, err) = proc.communicate()
    response = json.loads(output)
    if response.get('errorresponse'):
        print response['errorresponse']['errortext']
        return None
    return response['loginresponse']


def getKeys(hostname, loginresp, tmp_name):
    urlParam = '&response=json&id=' + \
        loginresp['userid'] + '&sessionkey=' + \
        encodeURIComponent(loginresp['sessionkey'])
    cmd = ['curl',
           '-v',
           '-H', 'Content-Type: application/json',
           '-b', tmp_name,
           '-X', 'POST',
           'http://' + hostname + ':8080/client/api/?command=listUsers' + urlParam]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, err) = proc.communicate()
    response = json.loads(output)
    logging.debug(response)
    user = response['listusersresponse']['user'][0]
    if not 'apikey' in user:
        return None
    return user['apikey'], user['secretkey']


def registerKeys(hostname, loginresp, tmp_name):
    urlParam = '&response=json&id=' + \
        loginresp['userid'] + '&sessionkey=' + \
        encodeURIComponent(loginresp['sessionkey'])
    cmd = ['curl',
           '-v',
           '-H', 'Content-Type: application/json',
           '-b', tmp_name,
           '-X', 'POST',
           'http://' + hostname + ':8080/client/api/?command=registerUserKeys' + urlParam]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, err) = proc.communicate()
    response = json.loads(output)
    logging.debug(response)
    return response


def getApiKey(hostname, username, password):
    tmp_cookie = tempfile.mkstemp(suffix=".cookie")
    tmp_name = tmp_cookie[1]
    loginresp = cloudLogin(hostname, username, password, tmp_name)
    if not loginresp:
        return None

    keypair = getKeys(hostname, loginresp, tmp_name)

    if not keypair:
        response = registerKeys(hostname, loginresp, tmp_name)
        keys = response['registeruserkeysresponse']
        if 'userkeys' in keys:
            keypair = keys['userkeys']['apikey'], keys['userkeys']['secretkey']

    os.remove(tmp_name)
    return keypair
