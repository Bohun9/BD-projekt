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
        response = client.get("/logout")
        assert "200" in response.status
        assert "user_id" not in session
        response = login(client, login="bad_login")
        assert "401" in response.status
