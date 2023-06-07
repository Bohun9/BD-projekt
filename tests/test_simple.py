import pytest
from protest.db import get_table


def test_register_member(app, client):
    response = client.post(
        "/register_member",
        data={
            "name": "Bob",
            "last_name": "Smith",
            "age": 50,
            "login": "login",
            "password": "password",
        },
    )
    assert "200" in response.status
    with app.app_context():
        members = get_table("OrganizationMember")
        assert len(members) == 1
        bob = members[0]
        assert bob["name"] == "Bob"
        assert bob["organizer_privilege"] == False
