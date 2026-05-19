from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from schema import HubCreate, HubResponse

router = APIRouter()

# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= ADD HUB =================
@router.post("/add", response_model=HubResponse)
def add_hub(hub_data: HubCreate, db: Session = Depends(get_db)):

    # clean name
    name = hub_data.name.strip().lower()

    # ✅ validate coordinates
    if not (-90 <= hub_data.latitude <= 90):
        raise HTTPException(status_code=400, detail="Invalid latitude")

    if not (-180 <= hub_data.longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid longitude")

    # ✅ check duplicate (case-insensitive safe)
    existing = db.query(models.Hub).filter(
        models.Hub.name.ilike(name)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Hub already exists")

    # create hub
    hub = models.Hub(
        name=name,
        latitude=hub_data.latitude,
        longitude=hub_data.longitude
    )

    db.add(hub)
    db.commit()
    db.refresh(hub)

    return hub


# ================= GET HUBS =================
@router.get("/", response_model=list[HubResponse])
def get_hubs(db: Session = Depends(get_db)):

    return db.query(models.Hub).all()