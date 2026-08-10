import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from main import app
from database.session import get_session

# Import models so SQLModel.metadata knows about the tables
from models.user import User
from models.product import Product


TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def override_get_session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(test_engine)

    app.dependency_overrides[get_session] = override_get_session

    yield

    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client