import pytest
from protest.db import get_table
from flask import session, g
import decimal


def add_data(auth, add):
    for person in ["A", "B", "C", "D"]:
        auth.register(
            name=person, login=person, org=True if person in ["A", "B"] else False
        )

    auth.login(login="A")
    add.action(title="A")
    auth.login(login="B")
    add.action(title="B")

    add.protest(
        action_id=1,
        start_time="2011-11-04T05:00:00",
        end_time="2011-11-04T06:00:00",
        coordinate_x=0,
        coordinate_y=0,
        boombox_number=4,
    )
    add.protest(
        action_id=1,
        start_time="2011-11-04T07:00:00",
        end_time="2011-11-04T08:00:00",
        coordinate_x=5,
        coordinate_y=0,
        boombox_number=3,
    )
    add.protest(
        action_id=2,
        start_time="2011-11-04T04:00:00",
        end_time="2011-11-04T10:00:00",
        coordinate_x=10,
        coordinate_y=0,
        boombox_number=2,
    )

    auth.login("B")
    add.participation(protest_id=1)
    auth.login("C")
    add.participation(protest_id=1)
    add.participation(protest_id=2)

    auth.login("C")
    add.report(protest_id=1, description="cc", rating=2)
    add.report(protest_id=2, description="CCC", rating=6)
    auth.login("B")
    add.report(protest_id=1, description="b", rating=7)

    add.guard()
    add.guard()
    add.protection(protest_id=1, guard_id=1)


def test_query_action_stats(auth, add, query):
    add_data(auth, add)
    response = query.action_stats()
    assert "200" in response.status
    actions = response.json
    assert len(actions) == 2
    assert actions[0]["title"] == "A"
    assert actions[0]["no_protest"] == 2
    assert actions[0]["no_people"] == 3
    assert actions[1]["title"] == "B"
    assert actions[1]["no_protest"] == 1
    assert actions[1]["no_people"] == 1


def test_query_participant_stats(auth, add, query):
    add_data(auth, add)
    response = query.participant_stats()
    assert "200" in response.status
    participants = response.json
    print(participants)
    assert len(participants) == 4
    assert participants[0]["name"] == "C"
    assert participants[1]["name"] == "B"
    assert participants[2]["name"] == "A"
    assert participants[3]["name"] == "D"
    assert participants[0]["no_protest"] == 2
    assert participants[1]["no_protest"] == 2
    assert participants[2]["no_protest"] == 2
    assert participants[3]["no_protest"] == 0
    assert participants[0]["all_report_length"] == 5
    assert participants[1]["all_report_length"] == 1
    assert participants[2]["all_report_length"] == 0
    assert participants[3]["all_report_length"] == 0


def test_query_organizer_stats(auth, add, query):
    add_data(auth, add)
    response = query.organizer_stats()
    assert "200" in response.status
    organizers = response.json
    print(organizers)
    assert len(organizers) == 2
    assert organizers[0]["name"] == "A"
    assert organizers[1]["name"] == "B"
    assert (
        decimal.Decimal(organizers[0]["avg_rating"]) - decimal.Decimal("5.0")
    ) < 0.0001
    assert (
        decimal.Decimal(organizers[1]["avg_rating"]) - decimal.Decimal("1.0")
    ) < 0.0001


def test_query_closest_protests(auth, add, query):
    add_data(auth, add)
    response = query.closest_protests(
        0, 0, "2011-11-04T03:00:00", "2011-11-04T11:00:00"
    )
    assert "200" in response.status
    assert response.json == [{"id": 1}, {"id": 2}, {"id": 3}]
    response = query.closest_protests(
        10, 0, "2011-11-04T03:00:00", "2011-11-04T11:00:00"
    )
    assert "200" in response.status
    assert response.json == [{"id": 3}, {"id": 2}, {"id": 1}]
    response = query.closest_protests(
        10, 0, "2011-11-04T05:00:00", "2011-11-04T07:00:00"
    )
    assert "200" in response.status
    assert response.json == [{"id": 1}]


def test_query_profitable_protests(auth, add, query):
    add_data(auth, add)
    response = query.profitable_protests(
        2, "2011-11-04T03:00:00", "2011-11-04T11:00:00"
    )
    assert "200" in response.status
    protests = response.json
    assert len(protests) == 3
    assert protests[0]["id"] == 2
    assert protests[1]["id"] == 1
    assert protests[2]["id"] == 3
    response = query.profitable_protests(
        1, "2011-11-04T03:00:00", "2011-11-04T11:00:00"
    )
    assert "200" in response.status
    protests = response.json
    assert len(protests) == 2
    assert protests[0]["id"] == 2
    assert protests[1]["id"] == 3


def test_query_indirect_friends(auth, add, query):
    add_data(auth, add)
    response = query.indirect_friends(1)
    assert response.json == [{"id": 1}, {"id": 2}, {"id": 3}]
    response = query.indirect_friends(2)
    assert response.json == [{"id": 1}, {"id": 2}, {"id": 3}]
    response = query.indirect_friends(3)
    assert response.json == [{"id": 1}, {"id": 2}, {"id": 3}]
    response = query.indirect_friends(4)
    assert response.json == [{"id": 4}]
