import os
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

# Point the app at an isolated SQLite file before any app module is imported.
_TEST_DB = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-bytes-long"
os.environ["FRONTEND_DIST"] = str(Path(tempfile.mkdtemp()) / "no-frontend")

from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.seed import DEMO_PASSWORD, seed_demo_users  # noqa: E402

ALICE, BOB, CAROL = "alice@ajaia.dev", "bob@ajaia.dev", "carol@ajaia.dev"


@pytest.fixture(autouse=True)
def fresh_database() -> Iterator[None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_demo_users(db)
    yield


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth(client: TestClient) -> Callable[[str], dict[str, str]]:
    """Return Authorization headers for a seeded user."""
    cache: dict[str, dict[str, str]] = {}

    def _headers(email: str) -> dict[str, str]:
        if email not in cache:
            res = client.post("/api/auth/login", json={"email": email, "password": DEMO_PASSWORD})
            assert res.status_code == 200, res.text
            cache[email] = {"Authorization": f"Bearer {res.json()['access_token']}"}
        return cache[email]

    return _headers
