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
from webargs.flaskparser import parser
from markupsafe import escape_silent as escape
from inflection import pluralize
from neomodel.exception import DoesNotExist

from grest.exceptions import HTTPException
from grest.global_config import QUERY_LIMIT
from grest.utils import serialize


def index(self, request):
    """
    Returns an specified number of nodes, with pagination (skip/limit)
    :param request: Flask's current request object (passed from gREST)
    :type: request
    :param skip: skips the specified amount of nodes (offset/start)
    :type: int
    :param limit: number of nodes to return (shouldn't be more than total nodes)
    :type: int
    """
    try:
        # patch __log
        self.__log = self._GRest__log

        primary_model = self.__model__.get("primary")
        __validation_rules__ = {
            "skip": fields.Int(required=False, validate=lambda s: s >= 0, missing=0),
            "limit": fields.Int(required=False, validate=lambda l: l >= 1 and l <= 100),
            "order_by": fields.Str(required=False, missing="?")
        }

        # parse input data (validate or not!)
        # noinspection PyBroadException
        try:
            query_data = parser.parse(__validation_rules__, request)
        except:
            self.__log.debug("Validation failed!")
            raise HTTPException(
                "One or more of the required fields is missing or incorrect.", 422)

        start = query_data.get("skip")
        if start:
            start = int(start)

        count = query_data.get("limit")
        if count:
            count = start + int(count)
        else:
            count = start + QUERY_LIMIT

        all_properties = [prop
                            for prop in primary_model.defined_properties().keys()]

        order_by = str(escape(
            query_data.get("order_by"))) or "?"

        if order_by:
            if order_by.startswith("-"):
                order_by_prop = order_by[1:]
            else:
                order_by_prop = order_by

            if order_by_prop not in all_properties and order_by_prop != "?":
                raise HTTPException(
                    "Selected property for ordering is invalid.", 404)

        total_items = len(primary_model.nodes)

        if total_items <= 0:
            raise HTTPException(
                "No " + primary_model.__name__.lower() + " exists.", 404)

        if start > total_items:
            raise HTTPException(
                "One or more of the required fields is incorrect.", 422)

        page = primary_model.nodes.order_by(order_by)[start:count]

        if page:
            return serialize({pluralize(primary_model.__name__.lower()):
                                [item.to_dict() for item in page]})
        else:
            raise HTTPException(
                "No " + primary_model.__name__.lower() + " exists.", 404)
    except DoesNotExist as e:
        self.__log.exception(e)
        raise HTTPException(
            "The requested item or relation does not exist.", 404)
