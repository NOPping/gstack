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

from gstack import app
from gstack import authentication
from gstack.services import requester
from gstack.controllers import errors
from flask import jsonify, request, url_for
import json


def _cloudstack_securitygroup_to_gce(response_item):
    rules = response_item['ingressrule']
    allowed = []
    sourceranges = []
    for rule in rules:
        ports = []
        for i in range(rule['startport'], rule['endport'] + 1):
            ports.append(str(i))
        allowed.append({
            "IPProtocol": rule['protocol'],
            "ports": ports
        })
        if 'cidr' in rule.keys():
            sourceranges.append(rule['cidr'])
    return ({
        "kind": "compute#firewall",
        "selfLink": '',
        "id": response_item['id'],
        "creationTimestamp": '',
        "name": response_item['name'],
        "description": response_item['description'],
        "network": '',
        "sourceRanges": sourceranges,
        "sourceTags": [
            ''
        ],
        "targetTags": response_item['tags'],
        "allowed": allowed
    })


@app.route('/compute/v1/projects/<projectid>/global/firewalls',
           methods=['GET'])
@authentication.required
def listsecuritygroups(projectid, authorization):
    command = 'listSecurityGroups'
    args = {}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = cloudstack_response

    app.logger.debug(
        'Processing request for aggregated list Firewalls\n'
        'Project: ' + projectid + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    firewalls = []
    if cloudstack_response['listsecuritygroupsresponse']:
        res = cloudstack_response['listsecuritygroupsresponse']
        for response_item in res['securitygroup']:
            firewalls.append(response_item)

    items = []
    for fw in firewalls:
        items.append(_cloudstack_securitygroup_to_gce(fw))

    populated_response = {
        'kind': 'compute#firewallList',
        'id': 'projects/' + projectid + '/global/firewalls',
        'selfLink': request.base_url,
        'items': items
    }

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/compute/v1/projects/<projectid>/global/firewalls/<firewall>', methods=['GET'])
@authentication.required
def getsecuritygroup(projectid, authorization, firewall):
    command = 'listSecurityGroups'
    args = {
        'securitygroupname': firewall
    }
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )
    cloudstack_response = cloudstack_response

    app.logger.debug(
        'Processing request for get Firewall\n'
        'Project: ' + projectid + '\n' +
        'Firewall: ' + firewall + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    if cloudstack_response['listsecuritygroupsresponse']:
        response_item = cloudstack_response[
            'listsecuritygroupsresponse']['securitygroup'][0]
        firewall = _cloudstack_securitygroup_to_gce(response_item)
        res = jsonify(firewall)
        res.status_code = 200

    else:
        func_route = url_for('getsecuritygroup', projectid=projectid,
                             firewall=firewall)
        res = errors.resource_not_found(func_route)

    return res


@app.route('/compute/v1/projects/<projectid>/global/firewalls/<firewall>', methods=['DELETE'])
@authentication.required
def deletesecuritygroup(projectid, authorization, firewall):
    command = 'deleteSecurityGroup'
    args = {'name': firewall}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = cloudstack_response

    app.logger.debug(
        'Processing request for deleting a Firewall \n'
        'Project: ' + projectid + '\n' +
        'Firewall: ' + firewall + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    # return Global Operations
    populated_response = {}

    res = jsonify(populated_response)
    res.status_code = 200
    return res


@app.route('/compute/v1/projects/<projectid>/global/firewalls', methods=['POST'])
@authentication.required
def createsecuritygroup(projectid, authorization):
    command = 'createSecurityGroup'
    res = json.loads(request.data)
    args = {'name': res['name'],
            'description': res['description']}
    cloudstack_response = requester.make_request(
        command,
        args,
        authorization.client_id,
        authorization.client_secret
    )

    cloudstack_response = cloudstack_response

    app.logger.debug(
        'Processing request for creating a Firewall \n'
        'Project: ' + projectid + '\n' +
        'Firewall: ' + res['name'] + '\n' +
        json.dumps(cloudstack_response, indent=4, separators=(',', ': '))
    )

    net_protocol_codes = {'1': 'icmp', '6': 'tcp', '17': 'udp'}

    rules = res['allowed']
    if rules is not []:
        for rule in rules:
            command = 'authorizeSecurityGroupIngress'
            args = {'securitygroupname': res['name'],
                    'protocol': net_protocol_codes[str(rule['IPProtocol'])],
                    'startport': rule['ports'][0],
                    'endport': rule['ports'][0],
                    'cidrlist': ','.join([cidr for cidr in
                                          res['sourceRanges']])}
            cloudstack_response = requester.make_request(
                command,
                args,
                authorization.client_id,
                authorization.client_secret
            )

            cloudstack_response = cloudstack_response

            app.logger.debug(
                'Processing request for adding a rule to a Firewall \n'
                'Project: ' + projectid + '\n' +
                'Firewall: ' + res['name'] + '\n' +
                json.dumps(cloudstack_response,
                           indent=4, separators=(',', ': '))
            )

    # return Global Operations
    populated_response = {}
    res = jsonify(populated_response)
    res.status_code = 200
    return res
