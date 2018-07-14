# -*- coding: utf8 -*-
#
# Copyright (C) 2018 Mostafa Moradian <mostafamoradian0@gmail.com>
#
# This file is part of grest.
#
# grest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# grest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with grest.  If not, see <http://www.gnu.org/licenses/>.
#

import json

import dicttoxml
import markupsafe
import requests
import yaml
from flask import current_app as app
from flask import jsonify, request

import .messages as msg
from . import global_config
from .exceptions import HTTPException


def make_request(url, json_data=None, method="post", headers=None):
    if (headers is None):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    try:
        func = getattr(requests, method)
        if (json_data):
            response = func(url, json=json_data, headers=headers)
        else:
            response = func(url, headers=headers)

        if (response.content):
            return json.loads(response.content)
    except Exception as e:
        app.ext_logger.exception(e)
        return None


def get_header(name):
    if (name in request.headers):
        return request.headers.get(markupsafe.escape(name))
    else:
        return None


def serialize(data):
    try:
        accept = get_header(global_config.ACCEPT)

        if accept == "application/json":
            return jsonify(data)
        elif accept == "text/yaml":
            return yaml.safe_dump(data)
        elif accept == "text/xml":
            return dicttoxml.dicttoxml(data)
        else:
            # return json if content-type is not set
            return jsonify(data)
    except Exception:
        return jsonify(errors=[msg.SERIALIZATION_EXCEPTION]), 500
