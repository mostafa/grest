# -*- coding: utf8 -*-
#
# Copyright (C) 2018 Mostafa Moradian <mostafamoradian0@gmail.com>
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

import json

import pytest
from examples.app import create_app
from flask import url_for

uid = ""


def test_index(client):
    res = client.get(url_for("index"))
    assert res.data == b"Hello World"


def test_api_index(client):
    """PersonsView:index"""
    res = client.get("/v1/persons")
    assert res.status_code == 404
    assert res.json == {"errors": ["No person exists."]}


def test_api_get(client):
    """PersonsView:get"""
    res = client.get("/v1/persons/6054ae614f674627b6eea6542f4d8e29")
    assert res.status_code == 404
    assert res.json == {"errors": [
        "Selected person does not exist or the provided information is invalid."]}


def test_api_post(client):
    """PersonsView:post"""
    global uid
    res = client.post("/v1/persons",
                      data=json.dumps({"first_name": "test1", "last_name": "test2"}),
                      headers={'content-type': 'application/json'})
    assert res.status_code == 200
    if ("uid" in res.json):
        uid = res.json["uid"]
    assert "uid" in res.json


def test_api_put(client):
    """PersonsView:put"""
    global uid
    res = client.put("/v1/persons/" + uid,
                     data=json.dumps({"first_name": "test3", "last_name": "test4"}),
                     headers={'content-type': 'application/json'})
    assert res.status_code == 200
    if ("uid" in res.json):
        uid = res.json["uid"]
    assert "uid" in res.json


def test_api_patch(client):
    """PersonsView:patch"""
    global uid
    res = client.patch("/v1/persons/" + uid,
                       data=json.dumps({"first_name": "test5"}),
                       headers={'content-type': 'application/json'})
    assert res.status_code == 200
    assert res.json == {"result": "OK"}


def test_api_delete(client):
    """PersonsView:delete"""
    global uid
    res = client.delete("/v1/persons/" + uid)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    app.threaded = True
    return app
