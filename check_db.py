import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


# 读取当前脚本旁边的 .env 文件
load_dotenv(Path(__file__).with_name(".env"))

# 建立数据库连接
with psycopg.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    connect_timeout=5,
) as connection:
    # 创建游标，用来执行 SQL
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO knowledge_bases (name, description)
            VALUES (%s, %s)
            RETURNING id, name, description
            """,
            ("Python创建的资料", "通过程序写入数据库"),
        )

        created = cursor.fetchone()

        print("新增记录：", created)