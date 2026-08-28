def test_deleting_project_owner_deletes_owned_project_tasks_and_memberships(
    client,
    register_user,
    auth_headers,
    create_project,
    add_project_member,
    create_task,
    delete_me,
    assert_no_project_memberships,
):
    register_user(username="owner")
    member = register_user(username="member")

    owner_headers = auth_headers(username="owner")
    member_headers = auth_headers(username="member")

    project = create_project(owner_headers)

    add_project_member(
        headers=owner_headers,
        project_id=project["project_id"],
        username=member["username"],
    )

    create_task(
        headers=owner_headers,
        project_id=project["project_id"],
    )

    delete_me(owner_headers)

    project_response = client.get(
        f"/projects/{project['project_id']}",
        headers=member_headers,
    )
    assert project_response.status_code == 404

    tasks_response = client.get(
        f"/projects/{project['project_id']}/tasks",
        headers=member_headers,
    )
    assert tasks_response.status_code == 404

    assert_no_project_memberships(project["project_id"])


def test_deleting_assignee_clears_task_assignee(
    client,
    task_workflow_setup,
    delete_me,
):
    setup = task_workflow_setup()

    response = client.patch(
        setup["url"],
        json={"status": "ready"},
        headers=setup["assignee_headers"],
    )
    assert response.status_code == 200, response.json()

    delete_me(setup["assignee_headers"])

    response = client.get(
        setup["url"],
        headers=setup["owner_headers"],
    )

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["assignee_id"] is None
    assert data["status"] == "ready"


def test_deleting_task_creator_reassigns_task_to_project_owner(
    client,
    register_user,
    auth_headers,
    create_project,
    add_project_member,
    create_task,
    delete_me,
):
    owner = register_user(username="owner")
    creator = register_user(username="creator")

    owner_headers = auth_headers(username="owner")
    creator_headers = auth_headers(username="creator")

    project = create_project(owner_headers)

    add_project_member(
        headers=owner_headers,
        project_id=project["project_id"],
        username=creator["username"],
    )

    task = create_task(
        headers=creator_headers,
        project_id=project["project_id"],
    )

    delete_me(creator_headers)

    response = client.get(
        f"/projects/{project['project_id']}/tasks/{task['task_id']}",
        headers=owner_headers,
    )

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["created_by"] == owner["user_id"]


def test_deleting_reviewer_clears_review_state(
    client,
    task_workflow_setup,
    delete_me,
):
    setup = task_workflow_setup(with_reviewer=True)

    response = client.patch(
        setup["url"],
        json={"status": "ready"},
        headers=setup["assignee_headers"],
    )
    assert response.status_code == 200, response.json()

    response = client.patch(
        setup["url"],
        json={"status": "in_progress"},
        headers=setup["assignee_headers"],
    )
    assert response.status_code == 200, response.json()

    response = client.patch(
        setup["url"],
        json={"status": "to_review"},
        headers=setup["assignee_headers"],
    )
    assert response.status_code == 200, response.json()

    delete_me(setup["reviewer_headers"])

    response = client.get(
        setup["url"],
        headers=setup["owner_headers"],
    )

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["reviewer_id"] is None
    assert data["review_status"] is None
    assert data["status"] == "in_progress"


def test_deleting_user_who_is_creator_and_reviewer_reassigns_and_clears_review(
    client,
    register_user,
    auth_headers,
    create_project,
    add_project_member,
    create_task,
    delete_me,
    move_task_to_done,
):
    owner = register_user(username="owner")
    assignee = register_user(username="assignee")
    reviewer_creator = register_user(username="reviewercreator")

    owner_headers = auth_headers(username="owner")
    assignee_headers = auth_headers(username="assignee")
    reviewer_creator_headers = auth_headers(username="reviewercreator")

    project = create_project(owner_headers)

    add_project_member(owner_headers, project["project_id"], assignee["username"])
    add_project_member(
        owner_headers, project["project_id"], reviewer_creator["username"]
    )

    task = create_task(
        headers=reviewer_creator_headers,
        project_id=project["project_id"],
        assignee_id=assignee["user_id"],
        reviewer_id=reviewer_creator["user_id"],
    )

    url = f"/projects/{project['project_id']}/tasks/{task['task_id']}"

    move_task_to_done(
        url=url,
        assignee_headers=assignee_headers,
        reviewer_headers=reviewer_creator_headers,
    )

    delete_me(reviewer_creator_headers)

    response = client.get(url, headers=owner_headers)

    assert response.status_code == 200, response.json()

    data = response.json()

    assert data["created_by"] == owner["user_id"]
    assert data["reviewer_id"] is None
    assert data["review_status"] is None
    assert data["status"] == "done"
