import pytest
from fastapi.testclient import TestClient

from app.db.dependencies import get_db
from app.db.session import SessionLocal, engine
from app.main import app
from app.modules.auth.security import create_access_token, hash_password
from app.modules.organizations.models import Membership, Organization, User


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def test_identity(db_session):
    organization = Organization(name="Test Organization")
    user = User(
        email="owner@example.com",
        full_name="Test User",
        password_hash=hash_password("TestPassword123!"),
        is_active=True,
    )

    db_session.add_all([organization, user])
    db_session.flush()

    membership = Membership(
        user_id=user.id,
        organization_id=organization.id,
        role="owner",
    )
    db_session.add(membership)
    db_session.flush()

    return {
        "user": user,
        "organization": organization,
        "membership": membership,
    }


@pytest.fixture
def organization_id(test_identity):
    return test_identity["organization"].id


@pytest.fixture
def client(db_session, test_identity):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    user = test_identity["user"]
    organization = test_identity["organization"]
    token = create_access_token(user.id, organization.id)

    try:
        with TestClient(app) as test_client:
            test_client.headers.update({"Authorization": f"Bearer {token}"})
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
