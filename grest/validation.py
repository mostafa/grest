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

from urllib.request import unquote

from markupsafe import escape_silent as escape
from webargs.flaskparser import parser

import grest.messages as msg
from grest.exceptions import HTTPException


def validate_input(validation_rules, request, location="json"):
    # parse input data (validate or not!)
    # noinspection PyBroadException
    try:
        query_data = parser.parse(validation_rules, request, location=location)
    except:
        raise HTTPException(msg.VALIDATION_FAILED, 422)

    if not query_data:
        # if a non-existent property is present or misspelled,
        # the json_data property is empty!
        raise HTTPException(msg.INVALID_PROPERTIES, 409)

    return query_data


def validate_models(self,
                    primary_id=None,
                    secondary_model_name=None,
                    secondary_id=None):

    class Primary:
        id = None
        model = None
        model_name = None
        selection_field = None

    class Secondary:
        id = None
        model = None
        model_name = None
        selection_field = None

    if primary_id:
        Primary.id = escape(unquote(primary_id))

    Primary.model = self.__model__.get("primary")
    Primary.model_name = Primary.model.__name__.lower()
    Primary.selection_field = self.__selection_field__.get("primary")

    if secondary_model_name:
        Secondary.model_name = escape(unquote(secondary_model_name))

        if secondary_id:
            Secondary.id = escape(unquote(secondary_id))

        Secondary.model = Secondary.selection_field = None

        if "secondary" in self.__model__:
            Secondary.model = self.__model__.get(
                "secondary").get(Secondary.model_name)

        if "secondary" in self.__selection_field__:
            Secondary.selection_fields = self.__selection_field__.get(
                "secondary")
            Secondary.selection_field = Secondary.selection_fields.get(
                Secondary.model_name)

        if all([Secondary.model_name is not None,
                Secondary.model is None]):
            raise HTTPException(msg.RELATION_DOES_NOT_EXIST, 404)

    return (Primary, Secondary)
