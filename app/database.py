import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


# database.py 位于 app 内，.env 位于项目根目录
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
        row_factory=dict_row,
    )