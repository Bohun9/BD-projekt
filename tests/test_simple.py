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


def test_register_member(app, auth):
    response = auth.register()
    assert "200" in response.status
    with app.app_context():
        members = get_table("OrganizationMember")
        assert len(members) == 1
        bob = members[0]
        assert bob["name"] == "Bob"
        assert bob["organizer_privilege"] == True


def test_login(client, auth):
    auth.register()
    with client:
        response = auth.login()
        assert "200" in response.status
        assert session["user_id"] == 1
        assert g.user is None
        response = auth.login()
        assert g.user is not None
        response = auth.logout()
        assert "200" in response.status
        assert "user_id" not in session
        response = auth.login(login="bad_login")
        assert "401" in response.status


def add_action(client):
    return client.post("/add/action", data={"title": "zwiekszamy podatki"})


def test_add_action(auth, add):
    auth.register()
    auth.login()
    response = add.action()
    assert "200" in response.status
    auth.logout()
    response = add.action()
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


def test_add_protest(app, auth, add):
    auth.register()
    auth.login()
    add.action()
    response = add.protest()
    assert "200" in response.status
    with app.app_context():
        assert len(get_table("Protest")) == 1

    response = add.participation()
    assert "200" in response.status

    response = add.report()
    assert "200" in response.status


def test_add_guard(auth, add):
    auth.register()
    auth.login()
    add.action()
    add.protest()
    response = add.guard()
    assert "200" in response.status
    response = add.protection()
    assert "200" in response.status


def test_query_participants(auth, add, query):
    auth.register()
    auth.login()
    add.action()
    add.protest()
    response = query.participants(1)
    assert "200" in response.status
    assert response.json[0]["name"] == "Bob"
