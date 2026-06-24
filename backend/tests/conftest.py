import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings

from main import app
from dal.database import get_db

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


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    run_test_migrations()
    yield


@pytest.fixture(autouse=True)
def clean_test_data():
    yield

    with test_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
