#!/usr/bin/env python
# encoding: utf-8
#Licensed to the Apache Software Foundation (ASF) under one
#or more contributor license agreements.  See the NOTICE file
#distributed with this work for additional information
#regarding copyright ownership.  The ASF licenses this file
#to you under the Apache License, Version 2.0 (the
#"License"); you may not use this file except in compliance
#with the License.  You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing,
#software distributed under the License is distributed on an
#"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#KIND, either express or implied.  See the License for the
#specific language governing permissions and limitations
#under the License.

import sys
import os
#potentially re-write requester. It was taken from cloudmonkey
import requester

from application import app
from flask import jsonify, Response, request

#re-write these based on app.config
apikey='apikey'
secretkey='secretkey'
path='/client/api'
host='localhost'
port='8080'
protocol='http'

@app.route('/')
def api_root():
    message = {
            'status': 200,
            'message': app.config["CLOUDSTACK_URL"]
    }
    resp = jsonify(message)
    resp.status_code = 200

    return resp

#this is just an example to show how to use different http verbs
@app.route('/user/<uuid>', methods=['GET','DELETE','PATCH'])
def user(uuid):
    if request.method =='GET':
        response, error = requester.make_request('listUsers',{'id':uuid},None,host,port,apikey,secretkey,protocol,path)
        return response
    elif request.method =='PATCH':
        data = request.json
        data['id']=uuid
        response, error = requester.make_request('updateUser',data,None,host,port,apikey,secretkey,protocol,path)
        return response
    else:
        response, error = requester.make_request('deleteUser',{'id':uuid},None,host,port,apikey,secretkey,protocol,path)
        return response

#show how to use post with json dict
@app.route('/user', methods=['GET','POST'])
def users():
    if request.method =='GET':
        return listusers()
    elif request.method =='POST':
        '''Need to pass a json dictionary in the request to feed to the update !!!'''
        response, error = requester.make_request('createUser',request.json,None,host,port,apikey,secretkey,protocol,path)
        return response
