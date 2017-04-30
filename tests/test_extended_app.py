import json
import pytest
from examples.extended_app import create_app


uid = ""
pet_id = ""


def test_api_index(client):
    res = client.get("/persons",
                     query_string={"skip": 10, "limit": 1},
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

    for uid in uid_list:
        res = client.delete("/persons/" + uid)
        assert res.status_code == 200
        assert res.json == {"result": "OK"}


def test_api_index_pets(client):
    """PetsView:index"""
    res = client.get("/pets")
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
                          {"first_name": "test1", "last_name": "test2", "phone_number": "123"}),
                      headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    if ("uid" in res.json):
        uid = res.json["uid"]
    assert "uid" in res.json

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
    """PetsView:get"""
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
    res = client.post("/persons/" + uid + "/pets/" + pet_id)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}


def test_api_post_person_adopts_pet_error(client):
    """PersonsView:post"""
    global pet_id, uid
    res = client.post("/persons/" + uid + "/pets/" + pet_id)
    assert res.status_code == 409
    assert res.json == {"errors": ["Relation exists!"]}


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
    assert "pets" in res.json and "pet_id" in res.json["pets"]


def test_api_get_persons_non_existing_pet(client):
    """PersonsView:!cars"""
    global pet_id, uid
    res = client.get("/persons/" + uid + "/pets/123123123123")
    assert res.status_code == 404
    assert "errors" in res.json


def test_api_person_no_longer_owns_pet(client):
    """PersonsView:delete"""
    global uid, pet_id
    res = client.delete("/persons/" + uid + "/pets/" + pet_id)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}


def test_api_delete_person(client):
    """PersonsView:delete"""
    global uid
    res = client.delete("/persons/" + uid)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}


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
