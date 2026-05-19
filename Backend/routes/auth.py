import bcrypt
import random
import time
import requests

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal
import models

router = APIRouter()

# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= OTP STORE =================
otp_store = {}
OTP_EXPIRY = 300  # 5 min


# ================= SCHEMAS =================
class PhoneRequest(BaseModel):
    phone: str

class VerifyRequest(BaseModel):
    phone: str
    otp: str

class ResetRequest(BaseModel):
    phone: str
    otp: str
    new_password: str


# ================= SAFE SMS FUNCTION =================
def send_sms(phone, otp):
    try:
        url = "https://api.msg91.com/api/v5/flow/"  # REAL API (replace if using other)

        payload = {
            "sender": "RDLIVE",
            "route": "4",
            "country": "91",
            "sms": [
                {
                    "message": f"Your OTP is {otp}",
                    "to": [phone]
                }
            ]
        }

        headers = {
            "authkey": "YOUR_API_KEY",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        print("📩 SMS RESPONSE:", response.text)

    except Exception as e:
        print("⚠️ SMS FAILED (OTP still valid):", e)


# ================= SEND OTP =================
@router.post("/forgot-password")
def forgot_password(data: PhoneRequest, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.phone == data.phone
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = str(random.randint(100000, 999999))

    # store OTP
    otp_store[data.phone] = {
        "otp": otp,
        "expiry": time.time() + OTP_EXPIRY,
        "verified": False
    }

    # phone format fix
    phone = "91" + data.phone

    # send SMS safely
    send_sms(phone, otp)

    print(f"📩 OTP for {data.phone}: {otp}")

    return {"message": "OTP sent successfully"}


# ================= VERIFY OTP =================
@router.post("/verify-otp")
def verify_otp(data: VerifyRequest):

    record = otp_store.get(data.phone)

    if not record:
        raise HTTPException(status_code=400, detail="OTP not found")

    if time.time() > record["expiry"]:
        otp_store.pop(data.phone, None)
        raise HTTPException(status_code=400, detail="OTP expired")

    if record["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    record["verified"] = True

    return {"message": "OTP verified successfully"}


# ================= RESET PASSWORD =================
@router.post("/reset-password")
def reset_password(data: ResetRequest, db: Session = Depends(get_db)):

    record = otp_store.get(data.phone)

    if not record:
        raise HTTPException(status_code=400, detail="OTP session not found")

    if not record.get("verified"):
        raise HTTPException(status_code=403, detail="OTP not verified")

    if record["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user = db.query(models.User).filter(
        models.User.phone == data.phone
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = bcrypt.hashpw(
        data.new_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user.password = hashed_password
    db.commit()

    otp_store.pop(data.phone, None)

    return {"message": "Password updated successfully"}