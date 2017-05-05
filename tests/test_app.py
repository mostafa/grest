from flask import url_for
import json
import pytest
from examples.app import create_app


uid = ""


def test_index(client):
    res = client.get(url_for("index"))
    assert res.data == b"Hello World"


def test_api_index(client):
    """PersonsView:index"""
    res = client.get("/persons")
    assert res.status_code == 404
    assert res.json == {"errors": ["No person exists."]}


def test_api_get(client):
    """PersonsView:get"""
    res = client.get("/persons/6054ae614f674627b6eea6542f4d8e29")
    assert res.status_code == 404
    assert res.json == {"errors": [
        "Selected person does not exist or the provided information is invalid."]}


def test_api_post(client):
    """PersonsView:post"""
    global uid
    res = client.post("/persons",
                      data=json.dumps({"first_name": "test1", "last_name": "test2"}),
                      headers={'content-type': 'application/json'})
    assert res.status_code == 200
    if ("uid" in res.json):
        uid = res.json["uid"]
    assert "uid" in res.json


def test_api_put(client):
    """PersonsView:put"""
    global uid
    res = client.put("/persons/" + uid,
                     data=json.dumps({"first_name": "test3", "last_name": "test4"}),
                     headers={'content-type': 'application/json'})
    assert res.status_code == 200
    if ("uid" in res.json):
        uid = res.json["uid"]
    assert "uid" in res.json


def test_api_patch(client):
    """PersonsView:patch"""
    global uid
    res = client.patch("/persons/" + uid,
                       data=json.dumps({"first_name": "test5"}),
                       headers={'content-type': 'application/json'})
    assert res.status_code == 200
    assert res.json == {"result": "OK"}


def test_api_delete(client):
    """PersonsView:delete"""
    global uid
    res = client.delete("/persons/" + uid)
    assert res.status_code == 200
    assert res.json == {"result": "OK"}


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    app.threaded = True
    return app
