from fastapi.testclient import TestClient

from main import app


client = TestClient(app)

def test_register_user():
    response = client.post(
        "/register",
        json={
            "username": "pytest_user",
            "email": "pytest@example.com",
            "password": "TestPass123",
            "full_name": "Pytest User",
            "is_admin": False,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "pytest_user"
    assert data["email"] == "pytest@example.com"
    assert "password" not in data


def test_duplicate_username():
    response = client.post(
        "/register",
        json={
            "username": "pytest_user",
            "email": "another@example.com",
            "password": "TestPass123",
            "full_name": "Another User",
            "is_admin": False,
        },
    )

    assert response.status_code == 409


def test_login():
    response = client.post(
        "/login",
        data={
            "username": "pytest_user",
            "password": "TestPass123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_password():
    response = client.post(
        "/login",
        data={
            "username": "pytest_user",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401

