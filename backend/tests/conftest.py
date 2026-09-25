import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["MAX_MODE"] = "mock"
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from infrastructure.persistence.models import Base, make_engine, make_session_factory
from infrastructure.seed import seed_database
from interfaces.main import app
import interfaces.deps as deps


@pytest.fixture()
def client():
    engine = make_engine(os.environ["DATABASE_URL"])
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    Session = make_session_factory(engine)
    session = Session()
    seed_database(session)
    session.close()

    deps._engine = engine
    deps.SessionLocal = Session
    deps._settings.database_url = os.environ["DATABASE_URL"]

    def override_get_db():
        db = Session()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[deps.get_db] = override_get_db
    # Avoid lifespan re-seeding a different connection during tests
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()
