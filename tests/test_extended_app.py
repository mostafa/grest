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
import xml.etree.ElementTree as ET

import pytest
import yaml
from examples.extended_app import create_app

uid = ""
pet_id = ""


def test_api_index(client):
    res = client.get("/persons",
                     query_string={"skip": 10, "limit": 1},
                     data="{}",
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 404


def test_api_index_validation_error(client):
    res = client.get("/persons",
                     query_string={"skip": "string", "limit": "string"},
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 422

    res = client.get("/persons",
                     query_string={"skip": -1},
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 422

    res = client.get("/persons",
                     query_string={"limit": -1},
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 422

    res = client.get("/persons",
                     query_string={"limit": 101},
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 422


def test_api_index_request_infinite_items(client):
    res = client.get("/persons",
                     query_string={"skip": 100000},
                     data="{}",
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 404
    assert "errors" in res.json


def test_api_index_request_non_existing_item(client):
    res = client.get("/persons",
                     query_string={"skip": 11, "limit": 0},
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 422
    assert "errors" in res.json


def test_api_index_skip_limit_order_by(client):
    uid_list = []

    for i in range(1, 11):
        res = client.post("/persons",
                          data=json.dumps(
                              {"first_name": str(i), "last_name": str(i + 1),
                               "phone_number": str(i * 2)}),
                          headers={"Content-Type": "application/json"})
        if "uid" in res.json:
            uid_list.append(res.json["uid"])

    assert len(uid_list) == 10

    # skip more than available
    res = client.get("/persons",
                     query_string={"skip": 11},
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 422
    assert "errors" in res.json

    # skip one item and return only one, ordered by first_name
    res = client.get("/persons",
                     query_string={"skip": 1, "limit": 1,
                                   "order_by": "first_name"},
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    assert "people" in res.json
    assert len(res.json["people"]) == 1
    assert res.json["people"][0]["first_name"] == "10"
    assert res.json["people"][0]["last_name"] == "11"

    # reverse sort order
    res = client.get("/persons",
                     query_string={"skip": 1, "limit": 1,
                                   "order_by": "-first_name"},
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    assert "people" in res.json

    # order by non existing property
    res = client.get("/persons",
                     query_string={"skip": 1, "limit": 1,
                                   "order_by": "prop1"},
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 404
    assert "errors" in res.json

    # get all persons in YAML format
    res = client.get("/persons",
                     data="''\n",  # empty string
                     query_string={"order_by": "first_name"},
                     headers={"Accept": "text/yaml"})
    assert res.status_code == 200
    data = yaml.load(res.data)
    assert "people" in data
    assert len(data["people"]) == 10
    assert data["people"][0]["first_name"] == "1"
    assert data["people"][0]["last_name"] == "2"

    # get all persons in XML format
    res = client.get("/persons",
                     query_string={"order_by": "first_name"},
                     headers={"Accept": "text/xml"})
    assert res.status_code == 200
    data = ET.fromstring(res.data)
    assert len(data.findall("people")) == 1
    assert len([i for i in data.iter("item")]) == 10

    # delete all persons by uid
    for uid in uid_list:
        res = client.delete("/persons/" + uid)
        assert res.status_code == 200
        assert res.json == {"result": "OK"}


def test_api_index_pets(client):
    """PetsView:index"""
    res = client.get("/pets", data="{}")
    assert res.status_code == 404
    assert res.json == {"errors": ["No pet exists."]}


def test_api_get_non_existing_pet(client):
    """PetsView:get"""
    res = client.get("/pets/6054ae614f674627b6eea6542f4d8e30111")
    assert res.status_code == 404
    assert "errors" in res.json


def test_api_post_person(client):
    """PersonsView:post"""
    global uid
    res = client.post("/persons",
                      data=json.dumps(
                          {"first_name": "test1", "last_name": "test2",
                          "phone_number": "123", "secret_field": "MY_SECRET"}),
                      headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    if ("uid" in res.json):
        uid = res.json["uid"]
    assert "uid" in res.json

    # check if `secret_field` is filtered
    assert "secret_field" not in res.json

    # post existing person
    res = client.post("/persons",
                      data=json.dumps(
                          {"first_name": "test1", "last_name": "test2", "phone_number": "123"}),
                      headers={"Content-Type": "application/json"})
    assert res.status_code == 409
    assert "errors" in res.json

    # test unique property exception
    res = client.post("/persons",
                      data=json.dumps(
                          {"first_name": "test1", "last_name": "test2", "phone_number": "123"}),
                      headers={"Content-Type": "application/json"})
    assert res.status_code == 409
    assert "errors" in res.json


def test_api_get_specific_person(client):
    """PersonsView:get"""
    global uid
    res = client.get("/persons/" + uid)
    assert res.status_code == 200


def test_api_post_validation_errors(client):
    """PersonsView:post"""
    res = client.post("/persons",
                      data=json.dumps(
                          {"first_name": 1, "last_name": 1}),
                      headers={"Content-Type": "application/json"})
    assert res.status_code == 422
    assert "errors" in res.json


def test_api_post_pet(client):
    """PetsView:post"""
    global pet_id
    res = client.post("/pets",
                      data=json.dumps({"name": "Puppy"}),
                      headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    if ("pet_id" in res.json):
        pet_id = res.json["pet_id"]
    assert "pet_id" in res.json


def test_api_post_person_adopts_pet(client):
    """PersonsView:post"""
    global pet_id, uid
    res = client.post("/persons/" + uid + "/pets/" + pet_id,
                      data=json.dumps({"adopted_since": 2018}),
                      headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    assert res.json == {"result": "OK"}


def test_api_post_person_adopts_pet_error(client):
    """PersonsView:post"""
    global pet_id, uid
    res = client.post("/persons/" + uid + "/pets/" + pet_id)
    assert res.status_code == 409
    assert res.json == {"errors": ["Relation exists."]}


def test_api_post_person_buys_nonexisting_car(client):
    """PersonsView:post"""
    global uid
    res = client.post("/persons/" + uid + "/cars/12323123123")
    assert res.status_code == 404
    assert "errors" in res.json


def test_api_get_owner_of_pet(client):
    """PetsView:owner"""
    global pet_id, uid
    res = client.get("/pets/" + pet_id + "/owner")
    assert res.status_code == 200
    if ("owner" in res.json):
        uid = res.json["owner"]["uid"]
    assert "owner" in res.json


def test_api_get_persons_pets(client):
    """PersonsView:owner"""
    global pet_id, uid
    res = client.get("/persons/" + uid + "/pets")
    assert res.status_code == 200
    assert res.json != {}
    assert "errors" not in res.json


def test_api_get_persons_non_existing_relation(client):
    """PersonsView:!cars"""
    global pet_id, uid
    res = client.get("/persons/" + uid + "/cars")
    assert res.status_code == 404
    assert "errors" in res.json


def test_api_get_persons_specific_pet(client):
    """PersonsView:!cars"""
    global pet_id, uid
    res = client.get("/persons/" + uid + "/pets/" + pet_id)
    assert res.status_code == 200
    assert "pet" in res.json and "pet_id" in res.json["pet"] and "relationship" in res.json["pet"]


def test_api_get_persons_non_existing_pet(client):
    """PersonsView:!cars"""
    global pet_id, uid
    res = client.get("/persons/" + uid + "/pets/123123123123")
    assert res.status_code == 404
    assert "errors" in res.json


def test_api_put_person_pet_and_relation(client):
    global uid
    global pet_id
    # disconnect pet from person and reconnects them
    res = client.put("/persons/" + uid + "/pets/" + pet_id)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}

    # delete old person and insert new one
    res = client.put("/persons/" + uid,
                     data=json.dumps(
                         {"first_name": "Alex", "last_name": "Douglas", "phone_number": "123456"}),
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    if ("uid" in res.json):
        uid = res.json["uid"]
    assert "uid" in res.json

    # validation error
    res = client.put("/persons/" + uid,
                     data=json.dumps(
                         {"first_name": 123, "last_name": "Douglas", "phone_number": "123456"}),
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 422
    assert "errors" in res.json

    # delete old pet and insert new one
    res = client.put("/pets/" + pet_id,
                     data=json.dumps({"name": "Puppy"}),
                     headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    if ("pet_id" in res.json):
        pet_id = res.json["pet_id"]
    assert "pet_id" in res.json

    # connect person and pet
    res = client.put("/persons/" + uid + "/pets/" + pet_id)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}

    # non-existing relation
    res = client.put("/persons/" + uid + "/cars/123123")
    assert res.status_code == 404
    assert "errors" in res.json


def test_api_patch_person(client):
    # Note: patch cannot update relations (use put instead)
    # update person's phone_number
    global uid
    res = client.patch("/persons/" + uid,
                       data=json.dumps(
                           {"phone_number": "654321"}),
                       headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    assert res.json == {"result": "OK"}

    # validation error
    res = client.patch("/persons/" + uid,
                       data=json.dumps(
                           {"first_name": 123}),
                       headers={"Content-Type": "application/json"})
    assert res.status_code == 422
    assert "errors" in res.json


def test_api_delete_relation(client):
    """PersonsView:delete"""
    global uid, pet_id
    res = client.delete("/persons/" + uid + "/pets/" + pet_id)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}

    # non-existing relation
    res = client.delete("/persons/" + uid + "/pets/" + pet_id)
    assert res.status_code == 404
    assert "errors" in res.json


def test_api_delete_person(client):
    """PersonsView:delete"""
    global uid
    res = client.delete("/persons/" + uid)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}

    # delete non-existing person
    res = client.delete("/persons/" + uid)
    assert res.status_code == 404
    assert "errors" in res.json


def test_api_delete_pet(client):
    """PetsView:delete"""
    global pet_id
    res = client.delete("/pets/" + pet_id)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    app.threaded = True
    return app
