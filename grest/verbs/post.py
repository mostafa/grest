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

from webargs import fields
from webargs.flaskparser import parser
from markupsafe import escape_silent as escape
from inflection import pluralize
from neomodel import db
from neomodel.exception import RequiredProperty, UniqueProperty, DoesNotExist

from grest.exceptions import HTTPException
from grest.global_config import QUERY_LIMIT
from grest.utils import serialize


def post(self, request, primary_id=None, secondary_model_name=None, secondary_id=None):
    """
    Updates an specified node or its relation (creates relation, if none exists)
    :param primary_id: unique id of the primary (source) node (model)
    :type: str
    :param secondary_model_name: name of the secondary (destination) node (model)
    :type: str
    :param secondary_id: unique id of the secondary (destination) node (model)
    :type: str
    """
    try:
        # patch __log
        self.__log = self._GRest__log

        if (primary_id):
            primary_id = unquote(primary_id)
        if (secondary_model_name):
            secondary_model_name = unquote(secondary_model_name)
        if (secondary_id):
            secondary_id = unquote(secondary_id)

        primary_model = self.__model__.get("primary")
        primary_selection_field = self.__selection_field__.get("primary")
        secondary_model = secondary_selection_field = None

        # check if there exists a secondary model
        if "secondary" in self.__model__:
            secondary_model = self.__model__.get(
                "secondary").get(secondary_model_name)

        if "secondary" in self.__selection_field__:
            secondary_selection_fields = self.__selection_field__.get(
                "secondary")
            secondary_selection_field = secondary_selection_fields.get(
                secondary_model_name)

        if secondary_model_name is not None and secondary_model_name not in self.__model__.get("secondary"):
            raise HTTPException("Selected relation does not exist.", 404)

        if not (primary_id and secondary_model and secondary_id):
            # user wants to add a new item
            try:
                # parse input data (validate or not!)
                if primary_model.__validation_rules__:
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

                item = primary_model.nodes.get_or_none(**json_data)

                if not item:
                    with db.transaction:
                        item = primary_model(**json_data).save()
                        item.refresh()
                    return serialize({primary_selection_field:
                                        getattr(item, primary_selection_field)})
                else:
                    raise HTTPException(
                        primary_model.__name__ + " exists!", 409)
            except UniqueProperty:
                raise HTTPException(
                    "Provided properties are not unique!", 409)

        if primary_id and secondary_model and secondary_id:
            # user either wants to update a relation or
            # has provided invalid information
            primary_selected_item = primary_model.nodes.get_or_none(
                **{primary_selection_field: str(escape(primary_id))})

            secondary_selected_item = secondary_model.nodes.get_or_none(
                **{secondary_selection_field: str(escape(secondary_id))})

            if primary_selected_item and secondary_selected_item:
                if hasattr(primary_selected_item, secondary_model_name):

                    relation = getattr(
                        primary_selected_item, secondary_model_name)

                    related_item = secondary_selected_item in relation.all()

                    if related_item:
                        raise HTTPException("Relation exists!", 409)
                    else:
                        # parse input data as relation's (validate or not!)
                        if (relation.definition["model"] is not None):
                            if (relation.definition["model"].__validation_rules__):
                                try:
                                    json_data = parser.parse(
                                        relation.definition["model"].__validation_rules__, request)
                                except:
                                    self.__log.debug("Validation failed!")
                                    raise HTTPException(
                                        "One or more of the required fields is missing or incorrect.", 422)
                            else:
                                json_data = request.get_json(silent=True)
                        else:
                            json_data = {}

                        with db.transaction:
                            if (json_data == {}):
                                related_item = relation.connect(
                                    secondary_selected_item)
                            else:
                                related_item = relation.connect(
                                    secondary_selected_item, json_data)

                        if related_item:
                            return serialize(dict(result="OK"))
                        else:
                            raise HTTPException("Selected " + secondary_model.__name__.lower(
                            ) + " does not exist or the provided information is invalid.", 404)
                else:
                    raise HTTPException("Selected " + secondary_model.__name__.lower(
                    ) + " does not exist or the provided information is invalid.", 404)
            else:
                raise HTTPException("Selected " + primary_model.__name__.lower(
                ) + " does not exist or the provided information is invalid.", 404)

        raise HTTPException("Invalid information provided.", 404)
    except DoesNotExist as e:
        self.__log.exception(e)
        raise HTTPException(
            "The requested item or relation does not exist.", 404)
    except RequiredProperty as e:
        self.__log.exception(e)
        raise HTTPException("A required property is missing.", 500)
