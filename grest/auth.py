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

from functools import wraps

from flask import current_app as app

from .exceptions import HTTPException
from .utils import serialize


def auth_exempt(func):
    @wraps(func)
    def exempt_requests(self, *args, **kwargs):
        """
        If a custom endpoint is going to be exempted from authentication and/or
        authorization, it should be decorated with auth_exempt decorator.
        """

        try:
            return func(self, *args, **kwargs)
        except HTTPException as e:
            return serialize({"errors": [e.message]}), e.status_code
        except Exception as e:
            return serialize({"errors": [str(e)]}), 500
    return exempt_requests


def authenticate(func):
    @wraps(func)
    def authenticate_requests(self, *args, **kwargs):
        """
        The authentication_function can be either empty, which
        results in all requests being taken as granted and authenticated.
        Otherwise the authentication_function must not return when
        the authentication is successful otherwise it should raise an exception
        explaining the error (containing message and status_code).
        """

        # authenticate users here!
        try:
            if hasattr(app, "authentication_function"):
                app.authentication_function(self)
                return func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        except HTTPException as e:
            return serialize({"errors": [e.message]}), e.status_code
        except Exception as e:
            return serialize({"errors": [str(e)]}), 500
    return authenticate_requests


def authorize(func):
    @wraps(func)
    def authorize_requests(self, *args, **kwargs):
        """
        The authorization_function can be either empty, which
        results in all requests being taken as granted and authorized.
        Otherwise the authorization_function must not return when
        the authorization is successful otherwise it should raise an exception
        explaining the error (containing message and status_code).
        """

        # authorize users here!
        try:
            if hasattr(app, "authorization_function"):
                app.authorization_function(self)
                return func(self, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)
        except HTTPException as e:
            return serialize({"errors": [e.message]}), e.status_code
        except Exception as e:
            return serialize({"errors": [str(e)]}), 500
    return authorize_requests
