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

import logging
import logging.handlers
import os

import markupsafe
import neomodel
from flask import Flask, jsonify
from flask_classful import route
from neomodel import (IntegerProperty, RelationshipFrom, RelationshipTo,
                      StringProperty, StructuredNode, StructuredRel,
                      UniqueIdProperty)
from webargs import fields

from grest import GRest, global_config, models, utils


class PetInfo(StructuredRel, models.Relation):
    """Pet Information Model (for relationship)"""
    adopted_since = IntegerProperty()


class Pet(StructuredNode, models.Node):
    """Pet model"""
    pet_id = UniqueIdProperty()
    name = StringProperty()
    owner = RelationshipFrom("User", "HAS_PET")


class User(StructuredNode, models.Node):
    """User model"""
    __validation_rules__ = {
        "first_name": fields.Str(),
        "last_name": fields.Str(),
        "secret_field": fields.Str(),
        "phone_number": fields.Str(required=True),
    }

    __filtered_fields__ = ["secret_field"]

    uid = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()
    phone_number = StringProperty(unique_index=True, required=True)

    secret_field = StringProperty(default="secret", required=False)

    pets = RelationshipTo(Pet, "HAS_PET", model=PetInfo)


class UsersView(GRest):
    """User's View (/users)"""
    __model__ = {"primary": User,
                 "secondary": {
                     "pets": Pet
                 }}
    __selection_field__ = {"primary": "uid",
                           "secondary": {
                               "pets": "pet_id"
                           }}


class PetsView(GRest):
    """Pet's View (/pets)"""
    __model__ = {"primary": Pet}
    __selection_field__ = {"primary": "pet_id"}

    @route("/<pet_id>/owner", methods=["GET"])
    def owner(self, pet_id):
        try:
            pet = Pet.nodes.get(**{self.__selection_field__.get("primary"):
                                   str(markupsafe.escape(pet_id))})

            if (pet):
                current_owner = pet.owner.get()
                if (current_owner):
                    return jsonify(owner=current_owner.to_dict()), 200
                else:
                    return jsonify(errors=["Selected pet has not been adopted yet!"]), 404
            else:
                return jsonify(errors=["Selected pet does not exists!"]), 404
        except:
            return jsonify(errors=["An error occurred while processing your request."]), 500


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "Hello World"

    neomodel.config.DATABASE_URL = global_config.DB_URL
    neomodel.config.AUTO_INSTALL_LABELS = True
    neomodel.config.FORCE_TIMEZONE = True  # default False

    if (global_config.LOG_ENABLED):
        logging.basicConfig(filename=os.path.abspath(os.path.join(
            global_config.LOG_LOCATION, global_config.LOG_FILENAME)), format=global_config.LOG_FORMAT)
        app.ext_logger = logging.getLogger()
        app.ext_logger.setLevel(global_config.LOG_LEVEL)
        handler = logging.handlers.RotatingFileHandler(
            os.path.abspath(os.path.join(
                global_config.LOG_LOCATION, global_config.LOG_FILENAME)),
            maxBytes=global_config.LOG_MAX_BYTES,
            backupCount=global_config.LOG_BACKUP_COUNT)
        app.ext_logger.addHandler(handler)
    else:
        app.ext_logger = app.logger

    UsersView.register(app, route_base="/users", trailing_slash=False)
    PetsView.register(app, route_base="/pets", trailing_slash=False)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
    # app.run(debug=True, threaded=True)
