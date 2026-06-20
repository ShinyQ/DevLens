import os
import tempfile

# Set DATABASE_URL before any devlens imports so pydantic-settings picks it up.
# Each test run gets its own temp file so tests are fully isolated.
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")
os.close(_test_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import devlens.db.models.project  # noqa: F401 — ensure models are registered
import devlens.db.models.analytics  # noqa: F401

from devlens.db.base import Base
from devlens.db.session import get_db
from devlens.main import create_app


@pytest.fixture(scope="function")
def db_engine():
    # StaticPool ensures all connections share the same in-memory SQLite DB
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_pragmas(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_engine):
    app = create_app()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=db_engine)

    with TestClient(app) as c:
        yield c
