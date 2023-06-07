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
