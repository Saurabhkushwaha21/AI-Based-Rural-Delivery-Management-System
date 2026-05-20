from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os

# ================= SECURITY CONFIG =================

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY is not set in environment variables")

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ================= PASSWORD =================

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# ================= JWT ACCESS TOKEN =================

def create_token(data: dict):
    to_encode = data.copy()

    to_encode.update({
        "exp": datetime.now(timezone.utc) + timedelta(hours=2),
        "iat": datetime.now(timezone.utc)
    })

    # ensure standard claim
    if "sub" not in to_encode:
        raise ValueError("JWT must include 'sub' (user id)")

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ================= DECODE TOKEN =================

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        print("JWT ERROR:", str(e))  # better debugging
        return None


# ================= EMAIL VERIFICATION TOKEN =================

def generate_verification_token(email: str):
    return jwt.encode(
        {
            "email": email,
            "type": "email_verification",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ================= VERIFY EMAIL TOKEN =================

def decode_verification_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "email_verification":
            return None

        return payload

    except JWTError as e:
        print("VERIFICATION TOKEN ERROR:", str(e))
        return None
    