def test_get_me_success(client, register_user, auth_headers):
    user = register_user(username="johnsmith")
    headers = auth_headers(username="johnsmith")

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200, response.json()

    data = response.json()

    assert data["user_id"] == user["user_id"]
    assert data["username"] == "johnsmith"
    assert data["email"] == "johnsmith@test.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_get_me_without_token_fails(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_delete_me_success(client, register_user, auth_headers):
    register_user(username="johnsmith")
    headers = auth_headers(username="johnsmith")

    response = client.delete("/users/me", headers=headers)

    assert response.status_code == 204
    assert response.content == b""


def test_deleted_user_token_no_longer_works(client, register_user, auth_headers):
    register_user(username="johnsmith")
    headers = auth_headers(username="johnsmith")

    delete_response = client.delete("/users/me", headers=headers)

    assert delete_response.status_code == 204

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "User for token not found"
