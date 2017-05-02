from datetime import datetime
from functools import wraps
import json
from itertools import chain
import copy

from flask import request, g, jsonify, current_app as app
import markupsafe
import requests
from webargs import fields
from neomodel import (relationship_manager, Property, StringProperty,
                      DateTimeProperty, DateProperty, EmailProperty,
                      BooleanProperty, ArrayProperty, IntegerProperty,
                      UniqueIdProperty, JSONProperty)
# import logging
# import os
from . import global_config


class Node(object):
    __validation_rules__ = {}
    __filtered_fields__ = []

    def __init__(self):
        super(self.__class__, self)
        self.__validation_rules__ = self.validation_rules

    def serialize(self):
        properties = copy.deepcopy(self.__dict__)
        blocked_properties = ["id", "password",
                              "current_otp", "validation_rules"]

        if self.__filtered_fields__:
            blocked_properties.extend(self.__filtered_fields__)

        removable_keys = set()
        for prop in properties.keys():
            # remove null key/values
            if properties[prop] is None:
                removable_keys.add(prop)

            # remove display functions for choices
            if prop.startswith("get_") and prop.endswith("_display"):
                removable_keys.add(prop)

            # remove relations for now!!!
            if isinstance(properties[prop], relationship_manager.ZeroOrMore):
                removable_keys.add(prop)

            # remove blocked properties, e.g. password, id, ...
            if prop in blocked_properties:
                removable_keys.add(prop)

        for key in removable_keys:
            properties.pop(key)

        return properties

    @property
    def validation_rules(self):
        """
        if the user has defined validation rules,
        return that, otherwise construct a set of
        predefined rules and return it.

        All internal GRest methods should use this property.
        """

        if len(self.__validation_rules__) > 0:
            # there is a set of user-defined validation rules
            return self.__validation_rules__

        model_types = [
            StringProperty, DateTimeProperty, DateProperty,
            EmailProperty, BooleanProperty, UniqueIdProperty,
            ArrayProperty, IntegerProperty, JSONProperty
        ]

        model_mapping = {
            IntegerProperty: fields.Int,
            StringProperty: fields.Str,
            BooleanProperty: fields.Bool,
            DateTimeProperty: fields.DateTime,
            DateProperty: fields.Date,
            EmailProperty: fields.Email,
            ArrayProperty: fields.List,
            JSONProperty: fields.Dict,
            UniqueIdProperty: fields.UUID
        }

        name = 0
        value = 1

        for field in self.__all_properties__:
            if type(field[value]) in model_types:
                if isinstance(field[value], ArrayProperty):
                    if field[value].unique_index:
                        # what it contains: Array of *String*
                        container = model_mapping[
                            type(field[value].unique_index)]
                    else:
                        # defaults to Raw for untyped ArrayProperty
                        container = fields.Raw

                    self.__validation_rules__[field[name]] = model_mapping[
                        type(field[value])](container,
                                            required=field[value].required)
                else:
                    self.__validation_rules__[field[name]] = model_mapping[
                        type(field[value])](required=field[value].required)

        return self.__validation_rules__


def authenticate(func):
    @wraps(func)
    def authenticate_requests(*args, **kwargs):
        if (global_config.DEBUG):
            app.ext_logger.info(
                request.endpoint.replace(":", "/").replace(".", "/").lower())
        # authenticate users here!
        if hasattr(app, "authentication_function"):
            app.authentication_function(global_config.X_AUTH_TOKEN)

        return func(*args, **kwargs)
    return authenticate_requests


def authorize(func):
    @wraps(func)
    def authorize_requests(*args, **kwargs):
        if (global_config.DEBUG):
            app.ext_logger.info(
                request.endpoint.replace(":", "/").replace(".", "/").lower())

        # authorize users here!
        if hasattr(app, "authorization_function"):
            app.authorization_function(global_config.X_AUTH_TOKEN)

        return func(*args, **kwargs)
    return authorize_requests


def make_request(url, json_data=None, method="post", headers=None):
    if (headers is None):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    try:
        func = getattr(requests, method)
        if (json_data):
            response = func(url, json=json_data, headers=headers)
        else:
            response = func(url, headers=headers)

        if (response.content):
            return json.loads(response.content)
    except Exception as e:
        app.ext_logger.exception(e)
        return None


def get_header(name):
    if (name in request.headers):
        return request.headers.get(markupsafe.escape(name))
    else:
        return None
