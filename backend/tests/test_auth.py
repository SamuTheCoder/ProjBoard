from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_register_user_success():
    payload = {
        "username": "johnsmith",
        "email": "johnsmith@test.com",
        "first_name": "John",
        "last_name": "Smith",
        "password": "Password123",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201, response.json()

    data = response.json()

    assert data["username"] == "johnsmith"
    assert data["email"] == "johnsmith@test.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Smith"
    assert "password" not in data
    assert "password_hash" not in data


def test_login_user_success():
    register_payload = {
        "username": "johnsmith",
        "email": "johnsmith@test.com",
        "first_name": "John",
        "last_name": "Smith",
        "password": "Password123",
    }

    register_response = client.post("/auth/register", json=register_payload)

    assert register_response.status_code == 201, register_response.json()

    login_payload = {
        "username": "johnsmith",
        "password": "Password123",
    }

    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 200, response.json()

    data = response.json()

    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"
