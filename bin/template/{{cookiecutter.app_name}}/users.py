# -*- coding: utf-8 -*-

from grest import GRest
from schema import User


class UsersView(GRest):
    __models__ = {"primary": User}
    __selection_field__ = {"primary": "uid"}
