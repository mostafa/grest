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
import os

import neomodel
from flask import Flask
from neomodel import StringProperty, StructuredNode, UniqueIdProperty
from webargs import fields

from grest import GRest, global_config, models, utils


# noinspection PyAbstractClass
class Person(StructuredNode, models.Node):
    """Person model"""
    __validation_rules__ = {
        "uid": fields.Str(),
        "first_name": fields.Str(),
        "last_name": fields.Str()
    }

    uid = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()


class PersonsView(GRest):
    """Person's View (/persons)"""
    __model__ = {"primary": Person}
    __selection_field__ = {"primary": "uid"}
    route_prefix = "/v1"  # API version


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "Hello World"

    neomodel.config.DATABASE_URL = global_config.DB_URL
    neomodel.config.AUTO_INSTALL_LABELS = True
    neomodel.config.FORCE_TIMEZONE = True  # default False
    # global_config.LOG_ENABLED = True

    if global_config.LOG_ENABLED:
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

    PersonsView.register(app, route_base="/persons", trailing_slash=False)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, threaded=True)
