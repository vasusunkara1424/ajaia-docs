"""Idempotent seed of demo accounts so reviewers can test sharing immediately."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User

DEMO_PASSWORD = "demo1234"
DEMO_USERS = (
    ("alice@ajaia.dev", "Alice Johnson"),
    ("bob@ajaia.dev", "Bob Martinez"),
    ("carol@ajaia.dev", "Carol Chen"),
)


def seed_demo_users(db: Session) -> None:
    existing = set(db.scalars(select(User.email)).all())
    for email, name in DEMO_USERS:
        if email not in existing:
            db.add(User(email=email, name=name, password_hash=hash_password(DEMO_PASSWORD)))
    db.commit()
