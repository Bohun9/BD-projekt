import pytest
from protest import create_app
from protest.db import init_db, get_cursor


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "DATABASE": "baza_test"})
    with app.app_context():  # get app config to get db name
        init_db()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions:
    def __init__(self, client):
        self.client = client

    def login(self, login="login", password="password"):
        return self.client.post("/login", data={"login": login, "password": password})

    def register(
        self,
        name="Bob",
        last_name="Smith",
        age=50,
        login="login",
        password="password",
        org=True,
    ):
        return self.client.post(
            "/register_member",
            data={
                "name": name,
                "last_name": last_name,
                "age": age,
                "login": login,
                "password": password,
                "secret": "org" if org else "bad_secret",
            },
        )

    def logout(self):
        return self.client.get("/logout")


class AddActions:
    def __init__(self, client):
        self.client = client

    def action(self, title="title"):
        return self.client.post("/add/action", data={"title": title})

    def protest(
        self,
        action_id=1,
        start_time="2011-11-04T00:05:23",
        town="Wroclaw",
        coordinate_x=0,
        coordinate_y=0,
        boombox_number=1,
    ):
        return self.client.post(
            "/add/protest",
            data={
                "action_id": action_id,
                "start_time": start_time,
                "town": town,
                "coordinate_x": coordinate_x,
                "coordinate_y": coordinate_y,
                "boombox_number": boombox_number,
            },
        )

    def participation(self, protest_id=1):
        return self.client.post("/add/participation", data={"protest_id": protest_id})

    def report(self, protest_id=1, rating=10, description="very cool"):
        return self.client.post(
            "/add/report",
            data={
                "protest_id": protest_id,
                "rating": rating,
                "description": description,
            },
        )

    def guard(self, name="Tom", last_name="Smith", weight=90, running_speed=21):
        return self.client.post(
            "/add/guard",
            data={
                "name": name,
                "last_name": last_name,
                "weight": weight,
                "running_speed": running_speed,
            },
        )

    def worldview(self, guard_id=1, action_id=1):
        return self.client.post(
            "/add/worldview", data={"guard_id": guard_id, "action_id": action_id}
        )

    def protection(self, guard_id=1, protest_id=1):
        return self.client.post(
            "/add/protection", data={"guard_id": guard_id, "protest_id": protest_id}
        )


class QueryActions:
    def __init__(self, client):
        self.client = client

    def participants(self, protest_id):
        return self.client.get(f"/query/participants/{protest_id}")

    def action_stats(self):
        return self.client.get(f"/query/action_stats")

    def participant_stats(self):
        return self.client.get(f"/query/participant_stats")

    def organizer_stats(self):
        return self.client.get(f"/query/organizer_stats")


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def add(client):
    return AddActions(client)


@pytest.fixture
def query(client):
    return QueryActions(client)
