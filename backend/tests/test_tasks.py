def test_create_task_success(
    client,
    register_user,
    auth_headers,
    create_project,
    create_task,
):
    owner = register_user(username="owner")
    headers = auth_headers(username="owner")

    project = create_project(headers)

    task = create_task(
        headers=headers,
        project_id=project["project_id"],
        task_name="Build task routes",
        priority=4,
    )

    assert task["task_name"] == "Build task routes"
    assert task["project_id"] == project["project_id"]
    assert task["created_by"] == owner["user_id"]
    assert task["priority"] == 4
    assert task["status"] == "backlog"
    assert task["review_status"] is None


def test_non_member_cannot_create_task(
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

    response = client.post(
        f"/projects/{project['project_id']}/tasks",
        json={
            "task_name": "Illegal task",
            "task_description": "Should fail",
            "priority": 3,
        },
        headers=outsider_headers,
    )

    assert response.status_code == 403


def test_list_project_tasks(
    client,
    register_user,
    auth_headers,
    create_project,
    create_task,
):
    register_user(username="owner")
    headers = auth_headers(username="owner")
    project = create_project(headers)

    create_task(headers, project["project_id"], task_name="Task One")
    create_task(headers, project["project_id"], task_name="Task Two")

    response = client.get(
        f"/projects/{project['project_id']}/tasks",
        headers=headers,
    )

    assert response.status_code == 200, response.json()

    data = response.json()
    assert len(data) == 2

    task_names = {task["task_name"] for task in data}
    assert task_names == {"Task One", "Task Two"}


def test_get_task_success(
    client,
    register_user,
    auth_headers,
    create_project,
    create_task,
):
    register_user(username="owner")
    headers = auth_headers(username="owner")
    project = create_project(headers)

    task = create_task(headers, project["project_id"])

    response = client.get(
        f"/projects/{project['project_id']}/tasks/{task['task_id']}",
        headers=headers,
    )

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["task_id"] == task["task_id"]
    assert data["project_id"] == project["project_id"]


def test_update_task_name_success(
    client,
    register_user,
    auth_headers,
    create_project,
    create_task,
):
    register_user(username="owner")
    headers = auth_headers(username="owner")
    project = create_project(headers)

    task = create_task(headers, project["project_id"])

    response = client.patch(
        f"/projects/{project['project_id']}/tasks/{task['task_id']}",
        json={
            "task_name": "Renamed task",
        },
        headers=headers,
    )

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["task_name"] == "Renamed task"


def test_create_task_with_invalid_assignee_fails(
    client,
    register_user,
    auth_headers,
    create_project,
):
    register_user(username="owner")
    headers = auth_headers(username="owner")
    project = create_project(headers)

    register_user(username="outsider")

    response = client.post(
        f"/projects/{project['project_id']}/tasks",
        json={
            "task_name": "Task with invalid assignee",
            "task_description": "Should fail",
            "assignee_id": 2,
            "priority": 3,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Assignee must be a member of this project"


def test_delete_task_success(
    client,
    register_user,
    auth_headers,
    create_project,
    create_task,
):
    register_user(username="owner")
    headers = auth_headers(username="owner")
    project = create_project(headers)

    task = create_task(headers, project["project_id"])

    delete_response = client.delete(
        f"/projects/{project['project_id']}/tasks/{task['task_id']}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/projects/{project['project_id']}/tasks/{task['task_id']}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_assignee_can_move_task_from_backlog_to_ready(
    client,
    task_workflow_setup,
):
    setup = task_workflow_setup()

    response = client.patch(
        setup["url"],
        json={"status": "ready"},
        headers=setup["assignee_headers"],
    )

    assert response.status_code == 200, response.json()
    assert response.json()["status"] == "ready"


def test_task_cannot_move_from_backlog_directly_to_done(
    client,
    task_workflow_setup,
):
    setup = task_workflow_setup()

    response = client.patch(
        setup["url"],
        json={"status": "done"},
        headers=setup["assignee_headers"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Task status cannot change from backlog to done"


def test_task_cannot_enter_review_without_reviewer(
    client,
    task_workflow_setup,
):
    setup = task_workflow_setup()

    client.patch(
        setup["url"],
        json={"status": "ready"},
        headers=setup["assignee_headers"],
    )

    client.patch(
        setup["url"],
        json={"status": "in_progress"},
        headers=setup["assignee_headers"],
    )

    response = client.patch(
        setup["url"],
        json={"status": "to_review"},
        headers=setup["assignee_headers"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "A task entering review must have a reviewer"


def test_task_entering_review_sets_review_status_pending(
    client,
    task_workflow_setup,
):
    setup = task_workflow_setup(with_reviewer=True)

    client.patch(
        setup["url"],
        json={"status": "ready"},
        headers=setup["assignee_headers"],
    )

    client.patch(
        setup["url"],
        json={"status": "in_progress"},
        headers=setup["assignee_headers"],
    )

    response = client.patch(
        setup["url"],
        json={"status": "to_review"},
        headers=setup["assignee_headers"],
    )

    assert response.status_code == 200, response.json()
    assert response.json()["status"] == "to_review"
    assert response.json()["review_status"] == "pending"


def test_task_cannot_be_done_without_approved_review(
    client,
    task_workflow_setup,
):
    setup = task_workflow_setup(with_reviewer=True)

    client.patch(
        setup["url"],
        json={"status": "ready"},
        headers=setup["assignee_headers"],
    )

    client.patch(
        setup["url"],
        json={"status": "in_progress"},
        headers=setup["assignee_headers"],
    )

    client.patch(
        setup["url"],
        json={"status": "to_review"},
        headers=setup["assignee_headers"],
    )

    response = client.patch(
        setup["url"],
        json={"status": "done"},
        headers=setup["assignee_headers"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "A task must be approved before it can be done"
