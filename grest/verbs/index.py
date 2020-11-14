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

from inflection import pluralize
from markupsafe import escape_silent as escape
from neomodel.exception import DoesNotExist
from webargs import fields

import grest.messages as msg
from grest.exceptions import HTTPException
from grest.global_config import QUERY_LIMIT
from grest.utils import serialize
from grest.validation import validate_input, validate_models


def index(self, request):
    try:
        # patch __log
        self.__log = self._GRest__log

        __validation_rules__ = {
            "skip": fields.Int(required=False,
                               validate=lambda skip: skip >= 0,
                               missing=0),

            "limit": fields.Int(required=False,
                                validate=lambda lim: lim >= 1 and lim <= 100,
                                missing=QUERY_LIMIT),

            "order_by": fields.Str(required=False,
                                   missing="?")
        }

        (primary, secondary) = validate_models(self)

        query_data = validate_input(__validation_rules__, request, location="query")
        skip = query_data.get("skip")
        limit = query_data.get("skip") + query_data.get("limit")
        order_by = escape(query_data.get("order_by"))

        if order_by:
            if order_by.startswith("-"):
                # select property for descending ordering
                order_by_prop = order_by[1:]
            else:
                # select property for ascending ordering
                order_by_prop = order_by

            primary_model_props = primary.model.defined_properties().keys()
            if all([order_by_prop not in primary_model_props,
                    order_by_prop != "?"]):
                raise HTTPException(msg.INVALID_ORDER_PROPERTY, 404)

        total_items = len(primary.model.nodes)

        if total_items <= 0:
            raise HTTPException(msg.NO_ITEM_EXISTS.format(
                model=primary.model_name), 404)

        if skip > total_items:
            raise HTTPException(msg.VALIDATION_FAILED, 422)

        items = primary.model.nodes.order_by(order_by)[skip:limit]

        if items:
            return serialize({pluralize(primary.model_name):
                              [item.to_dict() for item in items]})
        else:
            raise HTTPException(msg.NO_ITEM_EXISTS.format(
                model=primary.model_name), 404)
    except DoesNotExist as e:
        self.__log.exception(e.message)
        raise HTTPException(msg.ITEM_DOES_NOT_EXIST, 404)
