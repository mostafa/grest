# -*- coding: utf-8 -*-

from neomodel import StringProperty, StructuredNode, UniqueIdProperty
from webargs import fields
from grest import models


class User(StructuredNode, models.Node):
    """
    Person model
    """
    __validation_rules__ = {
        "username": fields.Str(),
        "password": fields.Str()
    }

    uid = UniqueIdProperty()
    username = StringProperty()
    password = StringProperty()
