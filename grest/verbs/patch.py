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

try:
    # For Python 3.0 and later
    from urllib.request import unquote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import unquote

from markupsafe import escape_silent as escape
from neomodel import db
from neomodel.exception import DoesNotExist
from webargs.flaskparser import parser

from grest.exceptions import HTTPException
from grest.utils import serialize


def patch(self, request, primary_id):
    """
    Partially updates a node
    :param primary_id: unique id of the primary (source) node (model)
    :type: str

    Note: updating relations via PATCH is not supported.
    """
    primary_id = unquote(primary_id)

    try:
        # patch __log
        self.__log = self._GRest__log

        primary_model = self.__model__.get("primary")
        primary_selection_field = self.__selection_field__.get("primary")

        if primary_model.__validation_rules__:
            # noinspection PyBroadException
            try:
                json_data = parser.parse(
                    primary_model.__validation_rules__, request)
            except:
                self.__log.debug("Validation failed!")
                raise HTTPException(
                    "One or more of the required fields is missing or incorrect.", 422)
        else:
            json_data = request.get_json(silent=True)

        if not json_data:
            # if a non-existent property is present or misspelled,
            # the json_data property is empty!
            raise HTTPException(
                "A property is invalid, missing or misspelled!", 409)

        if primary_id:
            selected_item = primary_model.nodes.get_or_none(
                **{primary_selection_field: str(escape(primary_id))})

            if selected_item:
                if json_data:
                    with db.transaction:
                        selected_item.__dict__.update(json_data)
                        updated_item = selected_item.save()
                        selected_item.refresh()

                    if updated_item:
                        return serialize(dict(result="OK"))
                    else:
                        raise HTTPException(
                            "There was an error updating your desired item.", 500)
                else:
                    raise HTTPException(
                        "Invalid information provided.", 404)
            else:
                raise HTTPException("Item does not exist.", 404)
        else:
            raise HTTPException(primary_model.__name__ +
                                " id is not provided or is invalid.", 404)
    except DoesNotExist as e:
        self.__log.exception(e)
        raise HTTPException(
            "The requested item or relation does not exist.", 404)
