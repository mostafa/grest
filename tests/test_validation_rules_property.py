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

from neomodel import fields as neomodel_fields  # type: ignore
from webargs import fields as webargs_fields  # type: ignore

import grest


class model(neomodel_fields.StructuredNode, grest.models.Node):
    GREEK = (
        ("A", "Alpha"),
        ("B", "Beta"),
        ("G", "Gamma")
    )

    uuid = neomodel_fields.UniqueIdProperty()
    string = neomodel_fields.StringProperty(required=True)
    choices = neomodel_fields.StringProperty(choices=GREEK)
    integer = neomodel_fields.IntegerProperty()
    json = neomodel_fields.JSONProperty()
    array_of_string = neomodel_fields.ArrayProperty(
        neomodel_fields.StringProperty())
    raw_data = neomodel_fields.ArrayProperty()
    date = neomodel_fields.DateProperty()
    datetime = neomodel_fields.DateTimeProperty()
    boolean = neomodel_fields.BooleanProperty()
    email = neomodel_fields.EmailProperty()


def test_validation_rules_property():
    instance = model()

    for rule in instance.__validation_rules__.items():
        assert isinstance(rule[1], webargs_fields.Field)
        if isinstance(rule[1], webargs_fields.List):
            assert isinstance(rule[1].container, webargs_fields.Field)
