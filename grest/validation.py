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

from webargs.flaskparser import parser

import .messages as msg
from .exceptions import HTTPException


def validate_input(validation_rules, request):
    # parse input data (validate or not!)
    # noinspection PyBroadException
    try:
        query_data = parser.parse(validation_rules, request)
    except:
        raise HTTPException(msg.VALIDATION_FAILED, 422)

    return query_data


# FIXME: *SELF* SHOULD NOT BE CHANGED!!!
def validate_models(self,
                    primary_id=None,
                    secondary_model_name=None,
                    secondary_id=None):
    primary_id = escape(unquote(primary_id))
    if (secondary_model_name):
        secondary_model_name = escape(unquote(secondary_model_name))
    if (secondary_id):
        secondary_id = escape(unquote(secondary_id))

    self.primary_model = self.__model__.get("primary")
    self.primary_model_name = self.primary_model.__name__.lower()
    self.primary_selection_field = self.__selection_field__.get("primary")
    self.secondary_model = self.secondary_selection_field = None

    if "secondary" in self.__model__:
        self.secondary_model = self.__model__.get(
            "secondary").get(secondary_model_name)

    if "secondary" in self.__selection_field__:
        secondary_selection_fields = self.__selection_field__.get(
            "secondary")
        self.secondary_selection_field = secondary_selection_fields.get(
            secondary_model_name)

    if all([self.secondary_model_name is not None,
            self.secondary_model is None]):
        raise HTTPException(msg.RELATION_DOES_NOT_EXIST, 404)
