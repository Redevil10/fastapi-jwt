import os

import pytest
from fastapi.testclient import TestClient

# set ENV before create the app, to make sure we are creating a test db
os.environ["ENV"] = "TEST"
from main import app  # noqa: E402


@pytest.fixture(scope="session")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="session", autouse=True)
def clear_db_teardown():
    # code before yield statement will execute before the first test
    yield None
    # code after yield statement will execute after the last test
    os.remove("fastapi_app_test.db")


# @pytest.fixture(scope="session")
# def superuser_access_token():
#     login_data = {"username": "super.user@example.com", "password": "passw0rd"}
#     response = requests.post("/auth/token", data=login_data)
#     yield response.json()["access_token"]
