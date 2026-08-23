import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from dal.models.project_member_model import ProjectMember

from core.config import settings
from dal.database import get_db
from main import app

TEST_DATABASE_URL = settings.TEST_DATABASE_URL

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def run_test_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    run_test_migrations()
    yield


@pytest.fixture(autouse=True)
def clean_test_data():
    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))

    yield

    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def register_user(client):
    def _register_user(
        username: str = "testuser",
        email: str | None = None,
        password: str = "Password123#",
        first_name: str = "Test",
        last_name: str = "User",
    ):
        payload = {
            "username": username,
            "email": email or f"{username}@test.com",
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
        }

        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201, response.json()
        return response.json()

    return _register_user


@pytest.fixture()
def login_user(client):
    def _login_user(
        username: str = "testuser",
        password: str = "Password123#",
    ):
        response = client.post(
            "/auth/login",
            data={
                "username": username,
                "password": password,
            },
        )

        assert response.status_code == 200, response.json()
        return response.json()

    return _login_user


@pytest.fixture()
def auth_headers(login_user):
    def _auth_headers(
        username: str = "testuser",
        password: str = "Password123#",
    ):
        token_data = login_user(username=username, password=password)
        token = token_data["access_token"]

        return {
            "Authorization": f"Bearer {token}",
        }

    return _auth_headers


@pytest.fixture()
def create_project(client):
    def _create_project(
        headers: dict,
        project_name: str = "Test Project",
        project_description: str = "Test project description",
    ):
        response = client.post(
            "/projects/",
            json={
                "project_name": project_name,
                "project_description": project_description,
            },
            headers=headers,
        )

        assert response.status_code == 201, response.json()
        return response.json()

    return _create_project


@pytest.fixture()
def add_project_member(client):
    def _add_project_member(
        headers: dict,
        project_id: int,
        user_id: int,
    ):
        response = client.post(
            f"/projects/{project_id}/members",
            json={"user_id": user_id},
            headers=headers,
        )

        assert response.status_code == 201, response.json()
        return response.json()

    return _add_project_member


@pytest.fixture()
def create_task(client):
    def _create_task(
        headers: dict,
        project_id: int,
        task_name: str = "Test Task",
        task_description: str = "Test task description",
        assignee_id: int | None = None,
        reviewer_id: int | None = None,
        priority: int = 3,
        task_deadline: str | None = None,
    ):
        response = client.post(
            f"/projects/{project_id}/tasks",
            json={
                "task_name": task_name,
                "task_description": task_description,
                "assignee_id": assignee_id,
                "reviewer_id": reviewer_id,
                "priority": priority,
                "task_deadline": task_deadline,
            },
            headers=headers,
        )

        assert response.status_code == 201, response.json()
        return response.json()

    return _create_task


@pytest.fixture()
def task_workflow_setup(
    register_user,
    auth_headers,
    create_project,
    add_project_member,
    create_task,
):
    def _task_workflow_setup(with_reviewer: bool = False):
        owner = register_user(username="owner")
        assignee = register_user(username="assignee")

        owner_headers = auth_headers(username="owner")
        assignee_headers = auth_headers(username="assignee")

        project = create_project(owner_headers)

        add_project_member(
            headers=owner_headers,
            project_id=project["project_id"],
            user_id=assignee["user_id"],
        )

        reviewer = None
        reviewer_headers = None
        reviewer_id = None

        if with_reviewer:
            reviewer = register_user(username="reviewer")
            reviewer_headers = auth_headers(username="reviewer")
            reviewer_id = reviewer["user_id"]

            add_project_member(
                headers=owner_headers,
                project_id=project["project_id"],
                user_id=reviewer["user_id"],
            )

        task = create_task(
            headers=owner_headers,
            project_id=project["project_id"],
            assignee_id=assignee["user_id"],
            reviewer_id=reviewer_id,
        )

        return {
            "owner": owner,
            "assignee": assignee,
            "reviewer": reviewer,
            "owner_headers": owner_headers,
            "assignee_headers": assignee_headers,
            "reviewer_headers": reviewer_headers,
            "project": project,
            "task": task,
            "url": f"/projects/{project['project_id']}/tasks/{task['task_id']}",
        }

    return _task_workflow_setup


@pytest.fixture()
def delete_me(client):
    def _delete_me(headers: dict):
        response = client.delete("/users/me", headers=headers)
        assert response.status_code == 204, (
            response.json() if response.content else None
        )
        return response

    return _delete_me


@pytest.fixture()
def move_task_to_done(client):
    def _move_task_to_done(
        url: str,
        assignee_headers: dict,
        reviewer_headers: dict,
    ):
        response = client.patch(
            url,
            json={"status": "ready"},
            headers=assignee_headers,
        )
        assert response.status_code == 200, response.json()

        response = client.patch(
            url,
            json={"status": "in_progress"},
            headers=assignee_headers,
        )
        assert response.status_code == 200, response.json()

        response = client.patch(
            url,
            json={"status": "to_review"},
            headers=assignee_headers,
        )
        assert response.status_code == 200, response.json()

        response = client.patch(
            url,
            json={"review_status": "approved"},
            headers=reviewer_headers,
        )
        assert response.status_code == 200, response.json()

        response = client.patch(
            url,
            json={"status": "done"},
            headers=assignee_headers,
        )
        assert response.status_code == 200, response.json()
        assert response.json()["status"] == "done"

        return response.json()

    return _move_task_to_done


@pytest.fixture()
def assert_no_project_memberships(db_session):
    def _assert_no_project_memberships(project_id: int):
        memberships = (
            db_session.execute(
                select(ProjectMember).where(ProjectMember.project_id == project_id)
            )
            .scalars()
            .all()
        )

        assert memberships == []

    return _assert_no_project_memberships
