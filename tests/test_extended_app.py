import json
import pytest
from examples.extended_app import create_app


uid = ""
pet_id = ""


def test_api_index_pets(client):
    """PetsView:index"""
    res = client.get("/pets")
    assert res.status_code == 404
    assert res.json == {"errors": ["No pet exists."]}


def test_api_get_pet(client):
    """PetsView:get"""
    res = client.get("/pets/6054ae614f674627b6eea6542f4d8e30")
    assert res.status_code == 404
    assert res.json == {"errors": [
        "Selected pet does not exist or the provided information is invalid."]}


def test_api_post_person(client):
    """PersonsView:post"""
    global uid
    res = client.post("/persons",
                      data=json.dumps(
                          {"first_name": "test1", "last_name": "test2"}),
                      headers={"Content-Type": "application/json"})
    assert res.status_code == 200
    if ("uid" in res.json):
        uid = res.json["uid"]
    assert "uid" in res.json


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
