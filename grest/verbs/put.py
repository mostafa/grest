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

from webargs.flaskparser import parser
from markupsafe import escape_silent as escape
from neomodel import db
from neomodel.exception import DoesNotExist

from grest.exceptions import HTTPException
from grest.utils import serialize


def put(self, request, primary_id, secondary_model_name=None, secondary_id=None):
    """
    Deletes and inserts a new node or a new relation (with data)
    :param request: Flask's current request object (passed from gREST)
    :type: request
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

        if primary_id and secondary_model_name is None and secondary_id is None:
            # a single item is going to be updated(/replaced) with the
            # provided JSON data
            selected_item = primary_model.nodes.get_or_none(
                **{primary_selection_field: str(escape(primary_id))})

            if selected_item:
                # parse input data (validate or not!)
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

                if json_data:
                    with db.transaction:
                        # delete and create a new one
                        selected_item.delete()  # delete old node and its relations
                        created_item = primary_model(
                            **json_data).save()  # create a new node

                        if created_item:
                            # if (self.__model__ == Post and g.user):
                            #     created_item.creator.connect(g.user)
                            #     created_item.save()
                            created_item.refresh()
                            return serialize({primary_selection_field:
                                                getattr(created_item, primary_selection_field)})
                        else:
                            raise HTTPException(
                                "There was an error creating your desired item.", 500)
                else:
                    raise HTTPException(
                        "Invalid information provided.", 404)
            else:
                raise HTTPException(
                    primary_model.__name__ + " does not exist.", 404)
        else:
            if primary_id and secondary_model_name and secondary_id:
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

                        all_relations = relation.all()

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
                            # remove all relationships
                            for each_relation in all_relations:
                                relation.disconnect(each_relation)

                            # add a new relationship with data
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
                    raise HTTPException(
                        "One of the selected models does not exist or the provided information is invalid.", 404)

            raise HTTPException("Invalid information provided.", 404)
    except DoesNotExist as e:
        self.__log.exception(e)
        raise HTTPException(
            "The requested item or relation does not exist.", 404)
