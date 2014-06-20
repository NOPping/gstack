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

import os
import glob

from flask import request

from gstack import helpers
from gstack.services import requester
from gstack.controllers import errors

__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + '/*.py')]


def filter_by_name(data, name):
    for item in data:
        if item['name'] == name:
            return item
        elif 'displayname' in item and item['displayname'] == name:
            return item

    return None


def _get_items(authorization, args=None):
    args['listAll'] = 'true'

    response = requester.make_request(
        args['command'],
        args,
        authorization.client_id,
        authorization.client_secret
    )
    response = response[response.keys()[0]]

    return response


def _get_requested_items(authorization, args, type, to_cloudstack, **kwargs):
    name = None
    filter = helpers.get_filter(request.args)

    if 'name' in filter:
        name = filter['name']

    items = []

    if name:
        cloudstack_item = get_item_with_name(
            authorization=authorization,
            name=name,
            args=args,
            type=type
        )
        if cloudstack_item:
            items.append(
                to_cloudstack(
                    cloudstack_response=cloudstack_item, **kwargs
                )
            )
    else:
        cloudstack_items = _get_items(authorization=authorization, args=args)
        if cloudstack_items:
            for cloudstack_item in cloudstack_items[type]:
                items.append(
                    to_cloudstack(
                        cloudstack_response=cloudstack_item, **kwargs)
                )

    return items


def get_item_with_name(authorization, name, args, type):
    response = _get_items(
        authorization=authorization,
        args=args
    )

    if 'count' in response:
        response = filter_by_name(
            data=response[type],
            name=name
        )
        return response
    else:
        return None


def get_item_with_name_or_error(authorization, name, args, type, func_route, to_cloudstack, **kwargs):
    cloudstack_item = get_item_with_name(authorization, name, args, type)

    if cloudstack_item:
        return helpers.create_response(to_cloudstack(
            cloudstack_response=cloudstack_item, **kwargs
        ))
    else:
        return errors.resource_not_found(func_route)


def describe_items_aggregated(authorization, args, type, gce_type, to_cloudstack, **kwargs):
    from gstack.controllers import zones
    items = {}

    zone_list = zones.get_zone_names(authorization=authorization)

    for zone in zone_list:
        kwargs['zone'] = zone
        zone_items = _get_requested_items(authorization, args, type, to_cloudstack, **kwargs)
        items['zone/' + zone] = {}
        if zone_items:
            items['zone/' + zone][gce_type] = zone_items
        else:
            items['zone/' + zone] = errors.no_results_found(zone)

    return items


def describe_items(authorization, args, type, to_cloudstack, **kwargs):
    items = _get_requested_items(authorization, args, type, to_cloudstack, **kwargs)

    return items
