def create_record(
    connection,
    username: str,
    password_hash: str,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            RETURNING id, username
            """,
            (username, password_hash),
        )

        user = cursor.fetchone()

    return user

def get_by_username(connection, username: str):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = %s
            """,
            (username,),
        )

        user = cursor.fetchone()

    return user

def get_by_id(connection, user_id: int):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, username
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )

        user = cursor.fetchone()

    return user