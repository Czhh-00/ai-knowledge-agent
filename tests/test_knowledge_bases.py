from fastapi.testclient import TestClient

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