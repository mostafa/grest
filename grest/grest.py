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

from __future__ import unicode_literals, absolute_import

import imp
import os
import sys

from autologging import logged
from flask import request
from flask_classful import FlaskView, route
from neomodel import StructuredNode

from .auth import authenticate, authorize
from .verbs.delete import delete
from .verbs.get import get
from .verbs.index import index
from .verbs.patch import patch
from .verbs.post import post
from .verbs.put import put

imp.reload(sys)

try:
    # For Python 3.0 and later
    os.environ["PYTHONIOENCODING"] = "utf-8"
except ImportError:
    # Fall back for Python 2
    sys.setdefaultencoding("utf-8")  # FIXME: a better way should be found!


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
        """
        Returns an specified number of nodes, with pagination (skip/limit)

        skip [int] skips the specified amount of nodes (offset/start)
        limit [int] number of nodes to return (no more than total nodes/items)
        """
        return index(self, request)

    @route("/<primary_id>", methods=["GET"])
    @route("/<primary_id>/<secondary_model_name>", methods=["GET"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["GET"])
    @authenticate
    @authorize
    def get(self, primary_id, secondary_model_name=None, secondary_id=None):
        """
        Returns an specified node or its related node
        primary_id [str] unique id of the primary (src) node (model)
        secondary_model_name [str] name of the secondary (dest) node (model)
        secondary_id [str] unique id of the secondary (dest) node (model)

        The equivalent cypher query would be (as an example):
        MATCH (u:User) WHERE n.user_id = "123456789" RETURN n
        Or:
        MATCH (u:User)-[LIKES]->(p:Post) WHERE n.user_id = "123456789" RETURN p
        """
        return get(self, primary_id, secondary_model_name, secondary_id)

    @route("", methods=["POST"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["POST"])
    @authenticate
    @authorize
    def post(self, primary_id=None, secondary_model_name=None, secondary_id=None):
        """
        Updates an specified node or its relation
        (creates relation, if none exists)
        primary_id [str] unique id of the primary (source) node (model)
        secondary_model_name [str] name of the secondary (destination) node (model)
        secondary_id [str] unique id of the secondary (destination) node (model)
        """
        return post(self, request, primary_id, secondary_model_name, secondary_id)

    @route("/<primary_id>", methods=["PUT"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["PUT"])
    @authenticate
    @authorize
    def put(self, primary_id, secondary_model_name=None, secondary_id=None):
        """
        Updates an specified node or its relation
        (delete old nodes and relations and creates new ones)
        primary_id [str] unique id of the primary (source) node (model)
        secondary_model_name [str] name of the secondary (destination) node (model)
        secondary_id [str] unique id of the secondary (destination) node (model)
        """
        return put(self, request, primary_id, secondary_model_name, secondary_id)

    @route("/<primary_id>", methods=["PATCH"])
    @authenticate
    @authorize
    def patch(self, primary_id):
        """
        Partially updates a node
        primary_id [str] unique id of the primary (source) node (model)

        [NOTE] updating relations via PATCH is not supported.
        """
        return patch(self, request, primary_id)

    @route("/<primary_id>", methods=["DELETE"])
    @route("/<primary_id>/<secondary_model_name>/<secondary_id>", methods=["DELETE"])
    @authenticate
    @authorize
    def delete(self, primary_id, secondary_model_name=None, secondary_id=None):
        """
        Deletes a node or its specific relation
        primary_id [str] unique id of the primary (source) node (model)
        secondary_model_name [str] name of the secondary (destination) node (model)
        secondary_id [str] unique id of the secondary (destination) node (model)
        """
        return delete(self, request, primary_id, secondary_model_name, secondary_id)
