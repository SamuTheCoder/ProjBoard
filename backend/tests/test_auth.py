def test_register_user_success(client):
    payload = {
        "username": "johnsmith",
        "email": "johnsmith@test.com",
        "first_name": "John",
        "last_name": "Smith",
        "password": "Password123#",
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


def test_register_duplicate_username_fails(client, register_user):
    register_user(username="johnsmith", email="john1@test.com")

    response = client.post(
        "/auth/register",
        json={
            "username": "johnsmith",
            "email": "john2@test.com",
            "first_name": "John",
            "last_name": "Smith",
            "password": "Password123#",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"


def test_register_duplicate_email_fails(client, register_user):
    register_user(username="john1", email="john@test.com")

    response = client.post(
        "/auth/register",
        json={
            "username": "john2",
            "email": "john@test.com",
            "first_name": "John",
            "last_name": "Smith",
            "password": "Password123#",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already exists"


def test_login_user_success(client, register_user):
    register_user(username="johnsmith", password="Password123#")

    response = client.post(
        "/auth/login",
        data={
            "username": "johnsmith",
            "password": "Password123#",
        },
    )

    assert response.status_code == 200, response.json()

    data = response.json()

    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"


def test_login_wrong_password_fails(client, register_user):
    register_user(username="johnsmith", password="Password123#")

    response = client.post(
        "/auth/login",
        data={
            "username": "johnsmith",
            "password": "WrongPassword123#",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_unknown_user_fails(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "ghost",
            "password": "Password123#",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"
