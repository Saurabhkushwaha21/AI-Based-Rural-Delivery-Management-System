from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/update-location")
def update_location(data: dict, db: Session = Depends(get_db)):

    record = db.query(models.AgentLocation).filter(
        models.AgentLocation.agent_id == data.get("agent_id")
    ).first()

    if not record:
        record = models.AgentLocation(
            agent_id=data.get("agent_id"),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            status=data.get("status", "idle"),
            current_order_id=data.get("order_id")
        )
        db.add(record)

    record.latitude = data.get("latitude")
    record.longitude = data.get("longitude")
    record.current_order_id = data.get("order_id")
    record.status = data.get("status", "idle")
    record.updated_at = datetime.utcnow()

    db.commit()
    return {"message": "Location updated"}


@router.get("/all")
def get_all_agents(db: Session = Depends(get_db)):

    agents = db.query(models.AgentLocation).all()

    return [
        {
            "agent_id": a.agent_id,
            "lat": a.latitude,
            "lon": a.longitude,
            "status": a.status,
            "order_id": a.current_order_id,
            "updated_at": a.updated_at
        }
        for a in agents
    ]