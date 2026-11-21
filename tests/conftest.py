from contextlib import contextmanager

import pytest

from app.routers import knowledge_bases, users
from app.database import get_connection


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch):
    """每个测试使用临时知识库表和用户表，结束后回滚。"""
    with get_connection() as connection:
        with connection.transaction(force_rollback=True):
            # 同名临时表只对当前连接可见，查询时会优先使用它。
            connection.execute(
                """
                CREATE TEMP TABLE knowledge_bases (
                    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    name VARCHAR(50) NOT NULL CHECK (length(name) >= 1),
                    description TEXT
                ) ON COMMIT DROP
                """
            )
            connection.execute(
                """
                CREATE TEMP TABLE users (
                    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE
                        CHECK (length(username) >= 3),
                    password_hash TEXT NOT NULL
                ) ON COMMIT DROP
                """
            )

            @contextmanager
            def test_connection():
                # 接口中的事务使用保存点，保持外层测试事务可以回滚。
                with connection.transaction():
                    yield connection

            monkeypatch.setattr(knowledge_bases, "get_connection", test_connection)
            monkeypatch.setattr(
                users,
                "get_connection",
                test_connection,
            )
            yield connection
