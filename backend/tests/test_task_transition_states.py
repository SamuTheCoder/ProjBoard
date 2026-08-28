def test_task_cannot_skip_status_steps(client, task_workflow_setup):
    setup = task_workflow_setup()

    response = client.patch(
        setup["url"],
        json={"status": "in_progress"},
        headers=setup["assignee_headers"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Task status cannot change from backlog to in_progress"
    )


def test_task_cannot_move_from_ready_directly_to_review(
    client,
    task_workflow_setup,
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
        json={"status": "to_review"},
        headers=setup["assignee_headers"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Task status cannot change from ready to to_review"
    )


def test_review_status_cannot_be_approved_before_review_phase(
    client,
    task_workflow_setup,
):
    setup = task_workflow_setup(with_reviewer=True)

    response = client.patch(
        setup["url"],
        json={"review_status": "approved"},
        headers=setup["reviewer_headers"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "A task can only be approved or rejected while it is in review"
    )


def test_changing_reviewer_resets_review_status(
    client,
    register_user,
    auth_headers,
    create_project,
    add_project_member,
    create_task,
):
    register_user(username="owner")
    assignee = register_user(username="assignee")
    reviewer_one = register_user(username="reviewerone")
    reviewer_two = register_user(username="reviewertwo")

    owner_headers = auth_headers(username="owner")
    assignee_headers = auth_headers(username="assignee")

    project = create_project(owner_headers)

    add_project_member(owner_headers, project["project_id"], assignee["username"])
    add_project_member(owner_headers, project["project_id"], reviewer_one["username"])
    add_project_member(owner_headers, project["project_id"], reviewer_two["username"])

    task = create_task(
        headers=owner_headers,
        project_id=project["project_id"],
        assignee_id=assignee["user_id"],
        reviewer_id=reviewer_one["user_id"],
    )

    url = f"/projects/{project['project_id']}/tasks/{task['task_id']}"

    client.patch(url, json={"status": "ready"}, headers=assignee_headers)
    client.patch(url, json={"status": "in_progress"}, headers=assignee_headers)
    client.patch(url, json={"status": "to_review"}, headers=assignee_headers)

    response = client.patch(
        url,
        json={"reviewer_id": reviewer_two["user_id"]},
        headers=owner_headers,
    )

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["reviewer_id"] == reviewer_two["user_id"]
    assert data["review_status"] is None


def test_done_task_cannot_be_updated(
    client,
    task_workflow_setup,
    move_task_to_done,
):
    setup = task_workflow_setup(with_reviewer=True)

    move_task_to_done(
        url=setup["url"],
        assignee_headers=setup["assignee_headers"],
        reviewer_headers=setup["reviewer_headers"],
    )

    response = client.patch(
        setup["url"],
        json={"task_name": "Should not change"},
        headers=setup["owner_headers"],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Completed tasks cannot be modified"
