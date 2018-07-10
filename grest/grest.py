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

from __future__ import unicode_literals
import os
import sys
import imp
imp.reload(sys)

try:
    # For Python 3.0 and later
    os.environ["PYTHONIOENCODING"] = "utf-8"
    from urllib.request import unquote
except ImportError:
    # Fall back to Python 2's urllib2
    sys.setdefaultencoding("utf-8")  # FIXME: a better way should be found! 
    from urllib2 import unquote

from markupsafe import escape_silent as escape
from inflection import pluralize
from flask import request
from flask_classful import FlaskView, route
from neomodel import db, StructuredNode
from neomodel.exception import RequiredProperty, UniqueProperty, DoesNotExist
from webargs.flaskparser import parser
from webargs import fields
from autologging import logged

from .global_config import QUERY_LIMIT
from .utils import serialize
from .auth import authenticate, authorize
from .verbs.index import index
from .verbs.get import get
from .verbs.post import post
from .verbs.put import put
from .exceptions import HTTPException


@logged
class GRest(FlaskView):
    """
    Base class for graph-based RESTful API development
    :param __model__: create mapping of nodes, relations and endpoints
    :type: dict
    :param __selection_field__: create mapping of selection fields for each node/relation
    :type: dict

    The are two keys to consider:
    __model__:
        primary: model containing source node
        secondary: mapping of endpoints to destination nodes

    For example, you have a User node and Post node.
    User posts a Post, and may like other's posts, so your __model__
    would look like this:
        __model__ = {"primary": User,
                     "secondary": {
                        "posts": Post,
                        "likes": Post
                     }}

    The selection field is the unique field that signifies a specific node
    or its related node(s). It works like the __primary_key__ and __foreign_key__
    property in other ORMs. The above example is completed with the following mapping:
    __selection_field__ = {"primary": "user_id",
                           "secondary": {
                                "posts": "post_id",
                                "likes": "post_id"
                           }}
    """
    __model__ = {"primary": StructuredNode, "secondary": {}}
    __selection_field__ = {"primary": "id", "secondary": {}}

    def __init__(self):
        super(self.__class__, self)

    @authenticate
    @authorize
    def index(self):
        return index(self, request)

    @route("/<primary_id>", methods=["GET"])
    @route("/<primary_id>/<secondary_model_name>", methods=["GET"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["GET"])
    @authenticate
    @authorize
    def get(self, primary_id, secondary_model_name=None, secondary_id=None):
        return get(self, primary_id, secondary_model_name, secondary_id)

    @route("", methods=["POST"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["POST"])
    @authenticate
    @authorize
    def post(self, primary_id=None, secondary_model_name=None, secondary_id=None):
        return post(self, request, primary_id, secondary_model_name, secondary_id)

    @route("/<primary_id>", methods=["PUT"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["PUT"])
    @authenticate
    @authorize
    def put(self, primary_id, secondary_model_name=None, secondary_id=None):
        return put(self, request, primary_id, secondary_model_name, secondary_id)

    @route("/<primary_id>", methods=["PATCH"])
    @authenticate
    @authorize
    def patch(self, primary_id):
        """
        Partially updates a node
        :param primary_id: unique id of the primary (source) node (model)
        :type: str

        Note: updating relations via PATCH is not supported.
        """
        primary_id = unquote(primary_id)

        try:
            primary_model = self.__model__.get("primary")
            primary_selection_field = self.__selection_field__.get("primary")

            if primary_model.__validation_rules__:
                # noinspection PyBroadException
                try:
                    json_data = parser.parse(
                        primary_model.__validation_rules__, request)
                except:
                    self.__log.debug("Validation failed!")
                    raise HTTPException("One or more of the required fields is missing or incorrect.", 422)
            else:
                json_data = request.get_json(silent=True)

            if not json_data:
                # if a non-existent property is present or misspelled,
                # the json_data property is empty!
                raise HTTPException("A property is invalid, missing or misspelled!", 409)

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
                            raise HTTPException("There was an error updating your desired item.", 500)
                    else:
                        raise HTTPException("Invalid information provided.", 404)
                else:
                    raise HTTPException("Item does not exist.", 404)
            else:
                raise HTTPException(primary_model.__name__ + " id is not provided or is invalid.", 404)
        except DoesNotExist as e:
            self.__log.exception(e)
            raise HTTPException("The requested item or relation does not exist.", 404)

    @route("/<primary_id>", methods=["DELETE"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["DELETE"])
    @authenticate
    @authorize
    def delete(self, primary_id, secondary_model_name=None, secondary_id=None):
        """
        Deletes a node or its specific relation
        :param primary_id: unique id of the primary (source) node (model)
        :type: str
        :param secondary_model_name: name of the secondary (destination) node (model)
        :type: str
        :param secondary_id: unique id of the secondary (destination) node (model)
        :type: str
        """
        try:
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
                selected_item = primary_model.nodes.get_or_none(
                    **{primary_selection_field: str(escape(primary_id))})

                if selected_item:
                    with db.transaction:
                        if selected_item.delete():
                            return serialize(dict(result="OK"))
                        else:
                            raise HTTPException("There was an error deleting the item.", 500)
                else:
                    raise HTTPException("Item does not exist.", 404)
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
                            related_item = secondary_selected_item in relation.all()

                            if not related_item:
                                raise HTTPException("Relation does not exist!", 409)
                            else:
                                with db.transaction:
                                    relation.disconnect(
                                        secondary_selected_item)

                                if secondary_selected_item not in relation.all():
                                    return serialize(dict(result="OK"))
                                else:
                                    raise HTTPException("There was an error removing the selected relation.", 500)
                        else:
                            raise HTTPException("Selected " + secondary_model.__name__.lower(
                            ) + " does not exist or the provided information is invalid.", 404)
                    else:
                        raise HTTPException("Selected " + primary_model.__name__.lower(
                        ) + " does not exist or the provided information is invalid.", 404)
                raise HTTPException(primary_model.__name__ + " id is not provided or is invalid.", 404)
        except DoesNotExist as e:
            self.__log.exception(e)
            raise HTTPException("The requested item or relation does not exist.", 404)
