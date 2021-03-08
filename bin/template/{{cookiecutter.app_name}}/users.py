# -*- coding: utf-8 -*-

from schema import User

from grest import GRest


class UsersView(GRest):
    __models__ = {"primary": User}
    __selection_field__ = {"primary": "uid"}
