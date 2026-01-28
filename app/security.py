import bcrypt


def _encode_password(password: str) -> bytes:
    return password.encode("utf-8")


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_encode_password(password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_encode_password(password), hashed_password.encode("utf-8"))
