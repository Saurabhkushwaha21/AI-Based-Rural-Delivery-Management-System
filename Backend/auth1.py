import bcrypt
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
import models, schema

from utils.security import create_token, generate_verification_token
from utils.email import send_verification_email

router = APIRouter()

# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= RATE LIMIT =================
last_sent_time = {}
RESEND_COOLDOWN = 60  # seconds


# ================= REGISTER =================
@router.post("/register")
def register(user: schema.UserCreate, db: Session = Depends(get_db)):

    existing = db.query(models.User).filter(
        (models.User.email == user.email) |
        (models.User.phone == user.phone)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    # hash password
    hashed_password = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # verification token
    token = generate_verification_token(user.email)

    # create user
    new_user = models.User(
        name=user.name,
        email=user.email.lower().strip(),
        phone=user.phone,
        password=hashed_password,
        role=user.role.lower(),
        verification_token=token,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # send email
    send_verification_email(user.email, token)

    return {
        "message": "User registered successfully. Please verify your email."
    }


# ================= LOGIN =================
@router.post("/login")
def login(data: schema.LoginSchema, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        (models.User.email == data.email) |
        (models.User.phone == data.phone)
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # verify password
    if not bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password.encode("utf-8")
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # verify email
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please verify your email first."
        )

    # create JWT
    token = create_token({
        "sub": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role
        }
    }


# ================= VERIFY EMAIL =================
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.verification_token == token
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )

    # already verified
    if user.is_verified:
        return {
            "message": "Email already verified"
        }

    # verify user
    user.is_verified = True
    user.verification_token = None

    db.commit()

    return {
        "message": "Email verified successfully"
    }


# ================= RESEND VERIFICATION =================
@router.post("/resend-verification")
def resend_verification(email: str, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.email == email.lower().strip()
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # already verified
    if user.is_verified:
        return {
            "message": "Email already verified"
        }

    # rate limit
    now = time.time()

    if (
        email in last_sent_time and
        now - last_sent_time[email] < RESEND_COOLDOWN
    ):
        raise HTTPException(
            status_code=429,
            detail="Please wait 60 seconds before requesting again"
        )

    # new token
    token = generate_verification_token(user.email)

    user.verification_token = token
    db.commit()

    # send email again
    send_verification_email(user.email, token)

    # save resend time
    last_sent_time[email] = now

    return {
        "message": "Verification email sent successfully"
    }
