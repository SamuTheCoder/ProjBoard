# ProjBoard
A Project Management REST API

## Development seed data

From `backend/`, install the requirements and seed the configured local PostgreSQL
database:

```bash
pip install -r requirements.txt
python -m scripts.seed
```

This appends 20 users, 8 projects, project memberships, and realistic tasks. Seed
accounts use deterministic usernames (`seed_user01`, `seed_user02`, ...) and share
the development-only password `ProjBoard123!`. The complete login list is written
to the gitignored `backend/seed_credentials.csv` file.

Useful options:

```bash
# Rebuild all application data from scratch (destructive)
python -m scripts.seed --reset

# Add another independent data set without deleting anything
python -m scripts.seed --prefix demo2 --users 50 --projects 15

# Avoid putting a custom password in shell history
PROJBOARD_SEED_PASSWORD='AnotherDevPassword123!' python -m scripts.seed --prefix demo3
```

The script refuses non-local database hosts unless `--allow-non-local` is supplied.
Never use the seed credentials in production.
