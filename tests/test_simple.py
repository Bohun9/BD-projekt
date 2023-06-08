import pytest
from protest.db import get_table
from flask import session, g


def register(client):
    return client.post(
        "/register_member",
        data={
            "name": "Bob",
            "last_name": "Smith",
            "age": 50,
            "login": "login",
            "password": "password",
            "secret": "org",
        },
    )


def login(client, login="login", password="password"):
    return client.post(
        "/login",
        data={
            "login": login,
            "password": password,
        },
    )


def logout(client):
    client.get("/logout")


def test_register_member(app, client):
    response = register(client)
    assert "200" in response.status
    with app.app_context():
        members = get_table("OrganizationMember")
        assert len(members) == 1
        bob = members[0]
        assert bob["name"] == "Bob"
        assert bob["organizer_privilege"] == True


def test_login(client):
    register(client)
    with client:
        response = login(client)
        assert "200" in response.status
        assert session["user_id"] == 1
        assert g.user is None
        response = login(client)
        assert g.user is not None
        logout(client)
        assert "200" in response.status
        assert "user_id" not in session
        response = login(client, login="bad_login")
        assert "401" in response.status


def add_action(client):
    return client.post("/add/action", data={"title": "zwiekszamy podatki"})


def test_add_action(client):
    register(client)
    login(client)
    response = add_action(client)
    assert "200" in response.status
    logout(client)
    response = client.post("/add/action", data={"title": "zwiekszamy podatki"})
    assert "401" in response.status


def add_protest(client):
    return client.post(
        "/add/protest",
        data={
            "action_id": 1,
            "start_time": "2011-11-04T00:05:23",
            "town": "Wroclaw",
            "coordinate_x": 1,
            "coordinate_y": 1,
            "boombox_number": 5,
        },
    )


def test_add_protest(app, client):
    register(client)
    login(client)
    add_action(client)
    response = add_protest(client)
    assert "200" in response.status
    with app.app_context():
        assert len(get_table("Protest")) == 1

    response = client.post(
        "/add/participation",
        data={
            "protest_id": 1,
        },
    )
    assert "200" in response.status

    response = client.post(
        "/add/report",
        data={
            "protest_id": 1,
            "rating": 10,
            "description": "good stuff",
        },
    )
    assert "200" in response.status


def test_add_guard(app, client):
    register(client)
    login(client)
    add_action(client)
    add_protest(client)
    response = client.post(
        "/add/guard",
        data={
            "name": "Tom",
            "last_name": "Smith",
            "weight": 100,
            "running_speed": 21,
        },
    )
    assert "200" in response.status
    response = client.post(
        "/add/protection",
        data={
            "guard_id": 1,
            "protest_id": 1,
        },
    )
    assert "200" in response.status


def test_query_participants(client):
    register(client)
    login(client)
    add_action(client)
    add_protest(client)
    response = client.get("/query/participants/1")
    assert "200" in response.status
    assert response.json[0]["name"] == "Bob"
