from pydantic import BaseModel, Field, EmailStr, model_validator, field_validator
from typing import Optional, Literal


# ================= USER =================
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)

    email: EmailStr

    phone: str = Field(..., min_length=10, max_length=15)

    password: str = Field(..., min_length=6, max_length=100)

    role: Literal["user", "admin", "agent"] = "user"

    # clean inputs
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.lower().strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not v.isdigit():
            raise ValueError("Phone must contain only numbers")
        return v


# ================= LOGIN =================
class LoginSchema(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        if v:
            return v.lower().strip()
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError("Phone must contain only numbers")
        return v

    @model_validator(mode="after")
    def check_phone_or_email(self):
        if not self.phone and not self.email:
            raise ValueError("Phone or Email is required")

        if self.phone and self.email:
            # optional rule (prevents confusion)
            raise ValueError("Use either phone OR email, not both")

        return self


# ================= ORDER =================
class OrderCreate(BaseModel):
    receiver: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=10, max_length=15)

    package_type: Optional[str] = None
    weight: Optional[float] = Field(default=None, gt=0)

    address: str = Field(..., min_length=5)

    latitude: float
    longitude: float


class OrderResponse(BaseModel):
    id: int
    receiver: str
    status: str
    hub_id: Optional[int]

    class Config:
        from_attributes = True


# ================= HUB =================
class HubCreate(BaseModel):
    name: str = Field(..., min_length=2)
    latitude: float
    longitude: float


class HubResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
        