from flask import request, g, jsonify, current_app as app
import markupsafe
import requests
from datetime import datetime
from functools import wraps
import json
from itertools import chain
import copy
from neomodel import relationship_manager
# import logging
# import os
import global_config


class Node(object):
    __validation_rules__ = None

    def serialize(self):
        properties = copy.deepcopy(self.__dict__)
        blocked_properties = ["id", "password", "current_otp"]

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

   # @property
    # def __validation_rules__(self):
    #     # if a class already has validation rules, return that!
    #     if (len(self.__validation_rules__) > 0):
    #         return self.__validation_rules__

    #     model_types = [
    #         # JSONProperty
    #         StringProperty, DateTimeProperty, DateProperty,
    #         EmailProperty, BooleanProperty,
    #         ArrayProperty, IntegerProperty
    #     ]

    #     model_mapping = {
    #         IntegerProperty: fields.Int,
    #         StringProperty: fields.Str,
    #         BooleanProperty: fields.Bool,
    #         DateTimeProperty: fields.DateTime,
    #         DateProperty: fields.Date,
    #         EmailProperty: fields.Str,
    #         ArrayProperty: fields.Raw,
    #         # JSONProperty: fields.Raw,
    #     }

    #     self.__validation_rules__ = {}
    #     all_fields = dir(self)
    #     for field in all_fields:
    #         if type(getattr(self, field)) in model_types:
    #             if not (field.startswith("_") and field.endswith("_")):
    #                 self.__validation_rules__[field] = model_mapping[
    #                     getattr(self, field)]()

    #     return self.__validation_rules__


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
