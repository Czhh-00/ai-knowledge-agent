from fastapi import APIRouter, HTTPException, Depends
from psycopg.errors import UniqueViolation

from app.database import get_connection
from app.repositories import users as user_repository
from app.schemas import UserCreate, UserRead, UserLogin, Token
from app.security import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError

router = APIRouter(
    prefix="/users",
    tags=["用户"],
)


@router.post("", status_code=201, response_model=UserRead)
def register_user(data: UserCreate):
    password_hash = hash_password(data.password)

    try:
        with get_connection() as connection:
            user = user_repository.create_record(
                connection,
                data.username,
                password_hash,
            )
    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="用户名已存在",
        )

    return user

@router.post("/login", response_model=Token)
def login_user(data: UserLogin):
    with get_connection() as connection:
        user = user_repository.get_by_username(
            connection,
            data.username,
        )
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
        )
    password_valid = verify_password(
        data.password,
        user["password_hash"]
    )
    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
        )
    return{
        "access_token": create_access_token(user["id"]),
        "token_type": "bearer",
    }


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    unauthorized = HTTPException(
        status_code=401,
        detail="登录凭证无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 没有提供有效格式的 Bearer 请求头
    if credentials is None:
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])

        if user_id <= 0:
            raise ValueError("用户编号无效")
    except (InvalidTokenError, ValueError, TypeError):
        raise unauthorized from None

    # 确认令牌对应的用户仍然存在
    with get_connection() as connection:
        user = user_repository.get_by_id(connection, user_id)

    if user is None:
        raise unauthorized

    return user

@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: dict = Depends(get_current_user),
):
    return current_user