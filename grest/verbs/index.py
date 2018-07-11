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

from webargs import fields
from markupsafe import escape_silent as escape
from inflection import pluralize
from neomodel.exception import DoesNotExist

from grest.exceptions import HTTPException
from grest.global_config import QUERY_LIMIT
from grest.utils import serialize, validate_input


def index(self, request):
    """
    Returns an specified number of nodes, with pagination (skip/limit)
    :param request: Flask's current request object (passed from gREST)
    :type: request
    :param skip: skips the specified amount of nodes (offset/start)
    :type: int
    :param limit: number of nodes to return (no more than total nodes/items)
    :type: int
    """
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

        primary_model = self.__model__.get("primary")

        query_data = validate_input(__validation_rules__, request)
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

            primary_model_props = primary_model.defined_properties().keys()
            if all([order_by_prop not in primary_model_props,
                    order_by_prop != "?"]):
                raise HTTPException(
                    "Selected property for ordering is invalid.", 404)

        total_items = len(primary_model.nodes)

        if total_items <= 0:
            raise HTTPException(
                "No " + primary_model.__name__.lower() + " exists.", 404)

        if skip > total_items:
            raise HTTPException(
                "One or more of the required fields is incorrect.", 422)

        items = primary_model.nodes.order_by(order_by)[skip:limit]

        if items:
            primary_model_name = pluralize(primary_model.__name__.lower())

            return serialize({primary_model_name:
                              [item.to_dict() for item in items]})
        else:
            raise HTTPException(
                "No " + primary_model.__name__.lower() + " exists.", 404)
    except DoesNotExist as e:
        self.__log.exception(e)
        raise HTTPException(
            "The requested item or relation does not exist.", 404)
