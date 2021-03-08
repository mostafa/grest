# -*- coding: utf-8 -*-

import os

DEBUG = bool(os.getenv("DEBUG", {{cookiecutter.DEBUG}}))  # type: ignore # noqa

IP_ADDRESS = os.getenv("IP_ADDRESS", "{{cookiecutter.IP_ADDRESS}}")
PORT = int(os.getenv("PORT", {{cookiecutter.PORT}}))  # type: ignore # noqa

VERSION = os.getenv("VERSION", "0.0.1")
SECRET_KEY = os.getenv("SECRET_KEY", "{{cookiecutter.SECRET_KEY}}")
DB_URL = os.getenv(
    "DB_URL", ("bolt://{{cookiecutter.NEO4J_USERNAME}}:{{cookiecutter.NEO4J_PASSWORD}}@"
               "{{cookiecutter.NEO4J_HOSTNAME}}:{{cookiecutter.NEO4J_BOLT_PORT}}"))

X_AUTH_TOKEN = "{{cookiecutter.X_AUTH_TOKEN}}"
ENABLE_DELETE_ALL = os.getenv(
    "ENABLE_DELETE_ALL", "{{cookiecutter.ENABLE_DELETE_ALL}}")
