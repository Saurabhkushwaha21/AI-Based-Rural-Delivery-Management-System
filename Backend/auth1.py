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


# ================= SIMPLE RATE LIMIT (RESEND) =================
last_sent_time = {}
RESEND_COOLDOWN = 60  # seconds


# ================= REGISTER =================
@router.post("/register")
def register(user: schema.UserCreate, db: Session = Depends(get_db)):

    if not user.email and not user.phone:
        raise HTTPException(status_code=400, detail="Email or phone required")

    existing = db.query(models.User).filter(
        (models.User.email == user.email) |
        (models.User.phone == user.phone)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    token = generate_verification_token(user.email)

    new_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=hashed_password,
        role=user.role.lower(),
        verification_token=token,
        is_verified=0
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_verification_email(user.email, token)

    return {"message": "User registered. Please verify email"}


# ================= LOGIN =================
@router.post("/login")
def login(data: schema.LoginSchema, db: Session = Depends(get_db)):

    if not data.email and not data.phone:
        raise HTTPException(status_code=400, detail="Email or phone required")

    user = db.query(models.User).filter(
        (models.User.email == data.email) |
        (models.User.phone == data.phone)
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(
        status_code=403,
        detail="Email not verified. Please verify your email first."
    )

    token = create_token({
        "sub": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role,
    })

    return {
        "access_token": token,
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
        raise HTTPException(status_code=400, detail="Invalid token")

    if user.is_verified == 1:
        return {"message": "Already verified"}

    user.is_verified = 1
    user.verification_token = None

    db.commit()

    return {"message": "Email verified successfully"}


# ================= RESEND VERIFICATION =================
@router.post("/resend-verification")
def resend_verification(email: str, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified == 1:
        return {"message": "Already verified"}

    # rate limit (avoid spam)
    now = time.time()
    if email in last_sent_time and now - last_sent_time[email] < RESEND_COOLDOWN:
        raise HTTPException(
            status_code=429,
            detail="Please wait 60 seconds before resending"
        )

    token = generate_verification_token(user.email)
    user.verification_token = token
    db.commit()

    send_verification_email(user.email, token)

    last_sent_time[email] = now

    return {"message": "Verification email sent again"}
