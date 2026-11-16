from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_knowledge_base():
    response = client.post(
        "/knowledge-bases",
        json={
            "name": "Python 学习资料",
            "description": "学习笔记",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert isinstance(data["id"], int)
    assert data["name"] == "Python 学习资料"
    assert data["description"] == "学习笔记"


def test_create_without_name():
    response = client.post(
        "/knowledge-bases",
        json={"description": "没有填写名称"},
    )

    assert response.status_code == 422

def test_create_empty_name():
    response = client.post(
        "/knowledge-bases",
        json={"name": ""},
    )

    assert response.status_code == 422

def test_knowledge_base_lifecycle():
    # 1. 创建知识库，并取得实际生成的 ID
    response = client.post(
        "/knowledge-bases",
        json={"name": "流程测试资料"},
    )
    assert response.status_code == 201
    knowledge_base_id = response.json()["id"]

    url = f"/knowledge-bases/{knowledge_base_id}"

    # 2. 查询刚创建的知识库
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()["name"] == "流程测试资料"

    # 3. 修改知识库
    response = client.put(
        url,
        json={
            "name": "修改后的资料",
            "description": "已经更新",
        },
    )
    assert response.status_code == 200

    # 4. 再次查询，确认修改已保存
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "id": knowledge_base_id,
        "name": "修改后的资料",
        "description": "已经更新",
    }

    # 5. 删除知识库
    response = client.delete(url)
    assert response.status_code == 200

    # 6. 删除后应该查不到
    response = client.get(url)
    assert response.status_code == 404


def test_update_only_requested_knowledge_base():
    first = client.post("/knowledge-bases", json={"name": "保留的资料"}).json()
    second = client.post("/knowledge-bases", json={"name": "待修改资料"}).json()

    response = client.put(
        f"/knowledge-bases/{second['id']}",
        json={"name": "O'Reilly 学习资料", "description": "已更新"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": second["id"],
        "name": "O'Reilly 学习资料",
        "description": "已更新",
    }
    assert client.get(f"/knowledge-bases/{first['id']}").json() == first
    assert client.get(f"/knowledge-bases/{second['id']}").json() == response.json()


def test_delete_only_requested_knowledge_base():
    first = client.post("/knowledge-bases", json={"name": "保留的资料"}).json()
    second = client.post("/knowledge-bases", json={"name": "待删除资料"}).json()

    response = client.delete(f"/knowledge-bases/{second['id']}")

    assert response.status_code == 200
    assert response.json() == {"message": "知识库已删除", "id": second["id"]}
    assert client.get("/knowledge-bases").json() == [first]
    assert client.get(f"/knowledge-bases/{second['id']}").status_code == 404
    assert client.delete(f"/knowledge-bases/{second['id']}").status_code == 404

def test_get_invalid_id():
    response = client.get("/knowledge-bases/abc")
    assert response.status_code == 422

def test_create_name_too_long():
    reponse = client.post(
        "/knowledge-bases",
        json={
            "name":"a"*51
        }
    )
    assert reponse.status_code == 422

def test_create_name_at_limit():
    reponse = client.post("/knowledge-bases", json={"name":"a"*50})
    assert reponse.status_code == 201
    data = reponse.json()
    assert data["name"] == "a"*50

@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_missing_knowledge_base(method):
    payload = {"name": "不存在的资料"} if method == "PUT" else None
    response = client.request(method, "/knowledge-bases/999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "知识库不存在"}
