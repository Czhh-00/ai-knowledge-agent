import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security import verify_password


client = TestClient(app)


def test_register_user_stores_password_hash(isolated_database):
    password = "study-password-123"
    response = client.post(
        "/users",
        json={"username": "learner001", "password": password},
    )

    assert response.status_code == 201
    user = response.json()
    assert isinstance(user["id"], int)
    # 响应中不应包含明文密码或密码哈希。
    assert user == {"id": user["id"], "username": "learner001"}

    stored_user = isolated_database.execute(
        "SELECT id, username, password_hash FROM users WHERE id = %s",
        (user["id"],),
    ).fetchone()
    assert stored_user is not None
    assert stored_user["username"] == user["username"]
    assert stored_user["password_hash"] != password
    assert verify_password(password, stored_user["password_hash"])
    assert not verify_password("wrong-password", stored_user["password_hash"])


def test_register_duplicate_username_keeps_original_user(isolated_database):
    original_password = "original-password"
    replacement_password = "replacement-password"
    first = client.post(
        "/users",
        json={"username": "learner001", "password": original_password},
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/users",
        json={"username": "learner001", "password": replacement_password},
    )
    assert duplicate.status_code == 409
    assert duplicate.json() == {"detail": "用户名已存在"}

    stored_users = isolated_database.execute(
        "SELECT id, username, password_hash FROM users ORDER BY id"
    ).fetchall()
    assert len(stored_users) == 1
    assert stored_users[0]["id"] == first.json()["id"]
    assert verify_password(original_password, stored_users[0]["password_hash"])
    assert not verify_password(replacement_password, stored_users[0]["password_hash"])

    # 唯一约束异常回滚后，后续注册仍能成功。
    another = client.post(
        "/users",
        json={"username": "learner002", "password": "another-password"},
    )
    assert another.status_code == 201
    assert another.json()["username"] == "learner002"


@pytest.mark.parametrize(
    ("username", "password"),
    [("u" * 3, "p" * 8), ("u" * 50, "p" * 128)],
    ids=["minimum-lengths", "maximum-lengths"],
)
def test_register_user_at_length_limits(username, password):
    response = client.post(
        "/users",
        json={"username": username, "password": password},
    )

    assert response.status_code == 201
    assert response.json() == {"id": response.json()["id"], "username": username}


@pytest.mark.parametrize(
    ("payload", "invalid_field"),
    [
        ({"password": "valid-password"}, "username"),
        ({"username": "learner001"}, "password"),
        ({"username": "ab", "password": "valid-password"}, "username"),
        ({"username": "u" * 51, "password": "valid-password"}, "username"),
        ({"username": "learner001", "password": "p" * 7}, "password"),
        ({"username": "learner001", "password": "p" * 129}, "password"),
    ],
    ids=[
        "missing-username",
        "missing-password",
        "short-username",
        "long-username",
        "short-password",
        "long-password",
    ],
)
def test_register_user_rejects_invalid_input(
    payload, invalid_field, isolated_database
):
    response = client.post("/users", json=payload)

    assert response.status_code == 422
    assert any(
        error["loc"] == ["body", invalid_field]
        for error in response.json()["detail"]
    )
    count = isolated_database.execute("SELECT count(*) AS total FROM users").fetchone()
    assert count["total"] == 0
