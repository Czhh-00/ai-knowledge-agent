from app.security import hash_password, verify_password


password = "study-password-123"
stored_hash = hash_password(password)

print("生成的哈希：", stored_hash)

print(
    "正确密码验证：",
    verify_password(password, stored_hash),
)

print(
    "错误密码验证：",
    verify_password("wrong-password", stored_hash),
)