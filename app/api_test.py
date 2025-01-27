import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

access_token = None
refresh_token = None
post_id = None

@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {access_token}"}


def test_signup():
    response = client.post(
        "/users/signup",
        json={
            "id": "test11",
            "email": "test11@example.com",
            "password": "password123"
        }
    )
    print(response.json())
    assert response.status_code == 200


def test_signup_duplicate():
    response = client.post(
        "/users/signup",
        json={
            "id": "test",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 409


def test_login():
    global access_token, refresh_token
    response = client.post(
        "/users/login",
        data={"id": "test", "password": "aaa"}
    )
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["token"]
    refresh_token = response.cookies.get("refresh_token")
    assert access_token is not None
    assert refresh_token is not None


def test_refresh_token():
    global access_token
    response = client.post(
        "/users/refresh"
    )
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["token"]
    assert access_token is not None


def test_create_post(auth_headers):
    global post_id
    response = client.post(
        "/posts",
        headers=auth_headers,
        json={
            "title": "Test Title",
            "content": "Test Content",
            "author_id": "test"
        }
    )
    assert response.status_code == 200
    post_id = response.json()["post_id"]
    assert post_id is not None


def test_get_post():
    print(post_id)
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Title"
    assert data["content"] == "Test Content"
    assert data["author_id"] == "test"


def test_get_posts():
    response = client.get("/posts")
    assert response.status_code == 200


def test_create_post_unauthorized():
    response = client.post(
        "/posts",
        json={"title": "Unauthorized Post", "content": "Should fail"}
    )
    assert response.status_code == 401


def test_get_nonexistent_post(auth_headers):
    response = client.get(f"/posts/99999", headers=auth_headers)
    assert response.status_code == 404


def test_refresh_token_invalid():
    client.cookies.clear()
    client.cookies.set("refresh_token", "invalid")
    response = client.post(
        "/users/refresh",
    )
    assert response.status_code == 401 or response.status_code == 500
