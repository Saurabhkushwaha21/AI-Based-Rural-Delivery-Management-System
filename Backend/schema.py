from pydantic import BaseModel, Field,EmailStr,model_validator
from typing import Optional,Literal

# ================= USER =================
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6)
    role: Literal["user", "admin", "agent"] = "user"  


class LoginSchema(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

    @model_validator(mode="after")
    def check_phone_or_email(self):
        if not self.phone and not self.email:
            raise ValueError("Phone or Email is required")
        return self
# ================= ORDER =================
class OrderCreate(BaseModel):
    receiver: str
    phone: str
    package_type: Optional[str] = None
    weight: Optional[float] = None
    address: str
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
    name: str
    latitude: float
    longitude: float


class HubResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True