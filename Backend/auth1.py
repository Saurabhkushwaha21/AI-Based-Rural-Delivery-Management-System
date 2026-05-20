import bcrypt
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

# ================= REGISTER =================
@router.post("/register")
def register(user: schema.UserCreate, db: Session = Depends(get_db)):

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

    return {"message": "User registered. Please verify email."}

# ================= LOGIN =================
@router.post("/login")
def login(data: schema.LoginSchema, db: Session = Depends(get_db)):

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

    if user.is_verified == 0:
        raise HTTPException(status_code=403, detail="Please verify your email")

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

    user.is_verified = 1
    user.verification_token = None
    db.commit()

    return {"message": "Email verified successfully"}