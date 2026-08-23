def test_create_project_success(client, register_user, auth_headers):
    register_user(username="owner")
    headers = auth_headers(username="owner")

    response = client.post(
        "/projects/",
        json={
            "project_name": "Test Project",
            "project_description": "A test project",
        },
        headers=headers,
    )

    assert response.status_code == 201, response.json()

    data = response.json()
    assert data["project_name"] == "Test Project"
    assert data["project_description"] == "A test project"
    assert data["owner_id"] == 1


def test_list_projects_for_user(client, register_user, auth_headers, create_project):
    register_user(username="owner")
    headers = auth_headers(username="owner")

    create_project(headers, project_name="Project One")
    create_project(headers, project_name="Project Two")

    response = client.get("/projects/", headers=headers)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert len(data) == 2
    assert data[0]["project_name"] in {"Project One", "Project Two"}
    assert data[1]["project_name"] in {"Project One", "Project Two"}


def test_get_project_success(client, register_user, auth_headers, create_project):
    register_user(username="owner")
    headers = auth_headers(username="owner")

    project = create_project(headers)

    response = client.get(
        f"/projects/{project['project_id']}",
        headers=headers,
    )

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["project_id"] == project["project_id"]
    assert data["project_name"] == project["project_name"]


def test_non_member_cannot_get_project(
    client,
    register_user,
    auth_headers,
    create_project,
):
    register_user(username="owner")
    owner_headers = auth_headers(username="owner")

    project = create_project(owner_headers)

    register_user(username="outsider")
    outsider_headers = auth_headers(username="outsider")

    response = client.get(
        f"/projects/{project['project_id']}",
        headers=outsider_headers,
    )

    assert response.status_code == 404


def test_update_project_success(client, register_user, auth_headers, create_project):
    register_user(username="owner")
    headers = auth_headers(username="owner")

    project = create_project(headers)

    response = client.patch(
        f"/projects/{project['project_id']}",
        json={
            "project_name": "Updated Project",
            "project_description": "Updated description",
        },
        headers=headers,
    )

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["project_name"] == "Updated Project"
    assert data["project_description"] == "Updated description"


def test_delete_project_success(client, register_user, auth_headers, create_project):
    register_user(username="owner")
    headers = auth_headers(username="owner")

    project = create_project(headers)

    delete_response = client.delete(
        f"/projects/{project['project_id']}",
        headers=headers,
    )

    assert delete_response.status_code == 200

    get_response = client.get(
        f"/projects/{project['project_id']}",
        headers=headers,
    )

    assert get_response.status_code == 404
