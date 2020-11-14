# -*- coding: utf-8 -*-
#
# Copyright (C) 2017- Mostafa Moradian <mostafamoradian0@gmail.com>
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

import dicttoxml
from markupsafe import escape_silent as escape
import yaml
from flask import jsonify, request

import grest.messages as msg
import grest.global_config as global_config


def get_header(name):
    if (name in request.headers):
        return request.headers.get(escape(name))
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
