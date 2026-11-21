def get_by_id(connection, knowledge_base_id: int):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, description
            FROM knowledge_bases
            WHERE id = %s
            """,
            (knowledge_base_id,),
        )

        knowledge_base = cursor.fetchone()

    return knowledge_base

def list_records(connection, keyword : str, limit: int, offset: int):
    with connection.cursor() as cursor:
        cursor.execute(
             """
            SELECT id, name, description
            FROM knowledge_bases
            WHERE NAME ILIKE %s
            ORDER BY id
            LIMIT %s OFFSET %s
            """,
            (f"%{keyword}%",limit, offset)
        )

        knowledge_bases = cursor.fetchall()

    return knowledge_bases

def create_record(
    connection,
    name: str,
    description: str | None,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO knowledge_bases (name, description)
            VALUES (%s, %s)
            RETURNING id, name, description
            """,
            (name, description),
        )

        knowledge_base = cursor.fetchone()

    return knowledge_base

def update_record(
    connection,
    knowledge_base_id: int,
    name: str,
    description: str | None,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE knowledge_bases
            SET name = %s, description = %s
            WHERE id = %s
            RETURNING id, name, description
            """,
            (name, description, knowledge_base_id),
        )

        knowledge_base = cursor.fetchone()

    return knowledge_base

def delete_record(
        connection,
        knowledge_base_id: int,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM knowledge_bases
            WHERE id = %s
            RETURNING id
            """,
            (knowledge_base_id,),
        )

        deleted = cursor.fetchone()

    return deleted
