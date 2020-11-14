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

from neomodel import *
from webargs import fields

import grest


class model(StructuredNode, grest.models.Node):
    GREEK = (
        ("A", "Alpha"),
        ("B", "Beta"),
        ("G", "Gamma")
    )

    uuid = UniqueIdProperty()
    string = StringProperty(required=True)
    choices = StringProperty(choices=GREEK)
    integer = IntegerProperty()
    json = JSONProperty()
    array_of_string = ArrayProperty(StringProperty())
    raw_data = ArrayProperty()
    date = DateProperty()
    datetime = DateTimeProperty()
    boolean = BooleanProperty()
    email = EmailProperty()


def test_validation_rules_property():
    instance = model()

    for rule in instance.__validation_rules__.items():
        assert isinstance(rule[1], fields.Field)
        if isinstance(rule[1], fields.List):
            assert isinstance(rule[1].container, fields.Field)
