def test_transfer_project_ownership_success(
    client,
    register_user,
    auth_headers,
    create_project,
    add_project_member,
):
    owner = register_user(username="owner")
    new_owner = register_user(username="newowner")

    owner_headers = auth_headers(username="owner")
    new_owner_headers = auth_headers(username="newowner")

    project = create_project(owner_headers)

    add_project_member(
        headers=owner_headers,
        project_id=project["project_id"],
        user_id=new_owner["user_id"],
    )

    response = client.patch(
        f"/projects/{project['project_id']}/members/{new_owner['user_id']}",
        headers=owner_headers,
    )

    assert response.status_code == 200, response.json()
    assert response.json()["user_id"] == new_owner["user_id"]
    assert response.json()["role"] == "owner"

    project_response = client.get(
        f"/projects/{project['project_id']}",
        headers=new_owner_headers,
    )

    assert project_response.status_code == 200, project_response.json()
    assert project_response.json()["owner_id"] == new_owner["user_id"]


def test_old_owner_can_no_longer_remove_members_after_transfer(
    client,
    register_user,
    auth_headers,
    create_project,
    add_project_member,
):
    old_owner = register_user(username="oldowner")
    new_owner = register_user(username="newowner")
    member = register_user(username="member")

    old_owner_headers = auth_headers(username="oldowner")

    project = create_project(old_owner_headers)

    add_project_member(old_owner_headers, project["project_id"], new_owner["user_id"])
    add_project_member(old_owner_headers, project["project_id"], member["user_id"])

    response = client.patch(
        f"/projects/{project['project_id']}/members/{new_owner['user_id']}",
        headers=old_owner_headers,
    )

    assert response.status_code == 200, response.json()

    response = client.delete(
        f"/projects/{project['project_id']}/members/{member['user_id']}",
        headers=old_owner_headers,
    )

    assert response.status_code == 403
