# security.py
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

from app.config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypass")

def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None
    return int(payload["sub"])