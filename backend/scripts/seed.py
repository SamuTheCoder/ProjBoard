"""Populate a local ProjBoard database with realistic development data.

Run from the backend directory:

    python -m scripts.seed --reset

All generated users share one development-only password. A gitignored CSV login
manifest is written after a successful commit so the accounts are easy to use.
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from faker import Faker
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from core.security import hash_password
from dal.database import SessionLocal, engine
from dal.models.project_member_model import ProjectMember, ProjectRole
from dal.models.project_model import Project
from dal.models.task_model import ReviewStatus, Task, TaskStatus
from dal.models.user_model import User

DEFAULT_PASSWORD = "ProjBoard123!"
DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "seed_credentials.csv"
LOCAL_DATABASE_HOSTS = {None, "", "localhost", "127.0.0.1", "::1"}


@dataclass(frozen=True)
class SeedOptions:
    users: int
    projects: int
    min_members: int
    max_members: int
    min_tasks: int
    max_tasks: int
    random_seed: int
    prefix: str
    password: str
    manifest: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed a local ProjBoard database using its SQLAlchemy models."
    )
    parser.add_argument("--users", type=int, default=20)
    parser.add_argument("--projects", type=int, default=8)
    parser.add_argument("--min-members", type=int, default=3)
    parser.add_argument("--max-members", type=int, default=8)
    parser.add_argument("--min-tasks", type=int, default=15)
    parser.add_argument("--max-tasks", type=int, default=40)
    parser.add_argument(
        "--seed",
        dest="random_seed",
        type=int,
        default=2026,
        help="Random seed; reuse it to generate the same fake data.",
    )
    parser.add_argument(
        "--prefix",
        default="seed",
        help="Prefix for generated usernames (default: seed).",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("PROJBOARD_SEED_PASSWORD", DEFAULT_PASSWORD),
        help=(
            "Shared password for generated accounts. Defaults to the "
            "PROJBOARD_SEED_PASSWORD environment variable or a development value."
        ),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Where to write the gitignored login CSV.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete all current application data before seeding.",
    )
    parser.add_argument(
        "--allow-non-local",
        action="store_true",
        help="Explicitly allow a non-local database host (dangerous).",
    )
    return parser.parse_args()


def validate_options(args: argparse.Namespace) -> SeedOptions:
    if args.users < 1 or args.projects < 1:
        raise ValueError("--users and --projects must be at least 1")
    if not 1 <= args.min_members <= args.max_members <= args.users:
        raise ValueError(
            "Member limits must satisfy 1 <= min-members <= max-members <= users"
        )
    if not 0 <= args.min_tasks <= args.max_tasks:
        raise ValueError("Task limits must satisfy 0 <= min-tasks <= max-tasks")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,37}", args.prefix):
        raise ValueError(
            "--prefix must start with a letter, contain only letters, numbers, "
            "underscores, or hyphens, and be at most 38 characters"
        )
    if (
        len(args.password) < 8
        or not re.search(r"[A-Z]", args.password)
        or not re.search(r"[a-z]", args.password)
        or not re.search(r"\d", args.password)
    ):
        raise ValueError(
            "The seed password must be at least 8 characters and contain an "
            "uppercase letter, a lowercase letter, and a number"
        )

    return SeedOptions(
        users=args.users,
        projects=args.projects,
        min_members=args.min_members,
        max_members=args.max_members,
        min_tasks=args.min_tasks,
        max_tasks=args.max_tasks,
        random_seed=args.random_seed,
        prefix=args.prefix,
        password=args.password,
        manifest=args.manifest.expanduser().resolve(),
    )


def ensure_safe_database(allow_non_local: bool) -> None:
    database_url = engine.url
    if database_url.get_backend_name() != "postgresql":
        raise RuntimeError(
            "The seed script only supports ProjBoard's PostgreSQL database"
        )

    host = database_url.host
    if host not in LOCAL_DATABASE_HOSTS and not allow_non_local:
        raise RuntimeError(
            f"Refusing to seed non-local database host {host!r}. "
            "Use --allow-non-local only if this is definitely disposable."
        )


def reset_database(db: Session) -> None:
    # PostgreSQL CASCADE follows the application's foreign keys and resets IDs.
    db.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    db.commit()


def ensure_seed_accounts_available(db: Session, options: SeedOptions) -> None:
    usernames = [
        f"{options.prefix}_user{number:02d}" for number in range(1, options.users + 1)
    ]
    emails = [f"{username}@example.com" for username in usernames]
    collision_count = db.scalar(
        select(func.count())
        .select_from(User)
        .where((User.username.in_(usernames)) | (User.email.in_(emails)))
    )
    if collision_count:
        raise RuntimeError(
            f"Seed accounts with prefix {options.prefix!r} already exist. "
            "Choose a different --prefix or use --reset for a clean rebuild."
        )


def create_users(
    db: Session,
    fake: Faker,
    options: SeedOptions,
    now: datetime,
) -> list[User]:
    users: list[User] = []
    for number in range(1, options.users + 1):
        first_name = fake.first_name()[:50]
        last_name = fake.last_name()[:50]
        username = f"{options.prefix}_user{number:02d}"
        users.append(
            User(
                username=username,
                email=f"{username}@example.com",
                password_hash=hash_password(options.password),
                first_name=first_name,
                last_name=last_name,
                created_at=now - timedelta(days=random.randint(15, 540)),
            )
        )

    db.add_all(users)
    db.flush()
    return users


def create_projects(
    db: Session,
    fake: Faker,
    users: list[User],
    options: SeedOptions,
    now: datetime,
) -> tuple[list[Project], dict[int, list[User]]]:
    projects: list[Project] = []
    members_by_project: dict[int, list[User]] = {}

    for number in range(1, options.projects + 1):
        owner = random.choice(users)
        created_at = now - timedelta(days=random.randint(5, 365))
        project = Project(
            project_name=f"Project {number:02d}: {fake.catch_phrase()}"[:100],
            project_description=fake.sentence(nb_words=12)[:255],
            owner_id=owner.user_id,
            created_at=created_at,
            updated_at=created_at + timedelta(days=random.randint(0, 4)),
        )
        db.add(project)
        db.flush()

        member_count = random.randint(options.min_members, options.max_members)
        other_users = [user for user in users if user.user_id != owner.user_id]
        selected_members = [owner, *random.sample(other_users, member_count - 1)]

        db.add_all(
            ProjectMember(
                project_id=project.project_id,
                user_id=user.user_id,
                role=(
                    ProjectRole.owner
                    if user.user_id == owner.user_id
                    else ProjectRole.member
                ),
                joined_at=created_at + timedelta(days=random.randint(0, 4)),
            )
            for user in selected_members
        )
        projects.append(project)
        members_by_project[project.project_id] = selected_members

    db.flush()
    return projects, members_by_project


TASK_ACTIONS = (
    "Design",
    "Implement",
    "Review",
    "Document",
    "Refactor",
    "Validate",
    "Deploy",
    "Investigate",
    "Optimize",
    "Test",
)

TASK_SUBJECTS = (
    "authentication flow",
    "project dashboard",
    "task filters",
    "calendar view",
    "member permissions",
    "database indexes",
    "API error handling",
    "mobile navigation",
    "notification settings",
    "release checklist",
)


def workflow_values(
    status: TaskStatus,
    members: list[User],
) -> tuple[int | None, int | None, ReviewStatus | None]:
    assignee = random.choice(members) if random.random() < 0.88 else None

    if status == TaskStatus.to_review:
        reviewer = random.choice(members)
        review_status = random.choices(
            [ReviewStatus.pending, ReviewStatus.approved], weights=[4, 1]
        )[0]
    elif status == TaskStatus.done:
        reviewer = random.choice(members)
        review_status = ReviewStatus.approved
    else:
        reviewer = random.choice(members) if random.random() < 0.45 else None
        review_status = None

    return (
        assignee.user_id if assignee else None,
        reviewer.user_id if reviewer else None,
        review_status,
    )


def create_tasks(
    db: Session,
    fake: Faker,
    projects: list[Project],
    members_by_project: dict[int, list[User]],
    options: SeedOptions,
    now: datetime,
) -> list[Task]:
    tasks: list[Task] = []
    statuses = list(TaskStatus)

    for project in projects:
        members = members_by_project[project.project_id]
        task_count = random.randint(options.min_tasks, options.max_tasks)

        for number in range(1, task_count + 1):
            status = random.choices(statuses, weights=[18, 18, 28, 18, 18])[0]
            assignee_id, reviewer_id, review_status = workflow_values(status, members)
            created_at = max(
                project.created_at,
                now
                - timedelta(days=random.randint(0, 120), hours=random.randint(0, 23)),
            )
            deadline = None
            if random.random() < 0.82:
                deadline = now + timedelta(days=random.randint(-30, 75))

            tasks.append(
                Task(
                    project_id=project.project_id,
                    task_name=(
                        f"{random.choice(TASK_ACTIONS)} "
                        f"{random.choice(TASK_SUBJECTS)} #{number}"
                    )[:100],
                    task_description=fake.paragraph(nb_sentences=3),
                    created_at=created_at,
                    updated_at=min(
                        now,
                        created_at + timedelta(days=random.randint(0, 14)),
                    ),
                    created_by=random.choice(members).user_id,
                    assignee_id=assignee_id,
                    reviewer_id=reviewer_id,
                    priority=random.randint(1, 5),
                    status=status,
                    review_status=review_status,
                    task_deadline=deadline,
                )
            )

    db.add_all(tasks)
    db.flush()
    return tasks


def write_manifest(path: Path, users: list[User], password: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=["user_id", "username", "email", "password", "name"],
        )
        writer.writeheader()
        for user in users:
            writer.writerow(
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "password": password,
                    "name": f"{user.first_name} {user.last_name}",
                }
            )
    path.chmod(0o600)


def main() -> None:
    args = parse_args()
    options = validate_options(args)
    ensure_safe_database(args.allow_non_local)

    random.seed(options.random_seed)
    fake = Faker()
    fake.seed_instance(options.random_seed)
    now = datetime.now(timezone.utc).replace(microsecond=0)

    with SessionLocal() as db:
        if args.reset:
            reset_database(db)
        else:
            ensure_seed_accounts_available(db, options)

        try:
            users = create_users(db, fake, options, now)
            projects, members_by_project = create_projects(
                db, fake, users, options, now
            )
            tasks = create_tasks(
                db,
                fake,
                projects,
                members_by_project,
                options,
                now,
            )
            db.commit()
            # Keep the session open while SQLAlchemy refreshes attributes that
            # expire on commit.
            write_manifest(options.manifest, users, options.password)
        except Exception:
            db.rollback()
            raise

    print("ProjBoard seed complete")
    print(f"  Users:   {len(users)}")
    print(f"  Projects:{len(projects):>4}")
    print(f"  Tasks:   {len(tasks)}")
    print(f"  Login:   {options.prefix}_user01 / {options.password}")
    print(f"  Accounts:{str(options.manifest):>1}")
    print(
        "The manifest contains development-only plaintext passwords; do not commit it."
    )


if __name__ == "__main__":
    main()
