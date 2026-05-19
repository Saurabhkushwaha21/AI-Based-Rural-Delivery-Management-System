from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal
from dependencies import get_current_user
import models

router = APIRouter()


# ================= SCHEMA =================
class AssignRequest(BaseModel):
    order_id: int
    agent_id: int


# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= ASSIGN DELIVERY =================
@router.post("/assign")
def assign_delivery(
    data: AssignRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    # optional: only admin can assign
    # if user["role"] != "admin":
    #     raise HTTPException(403, "Only admin can assign")

    order = db.query(models.Order).filter(
        models.Order.id == data.order_id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # ❌ prevent re-assignment
    if order.status in ["assigned", "delivered"]:
        raise HTTPException(
            status_code=400,
            detail="Order already assigned or delivered"
        )

    # update order
    order.status = "assigned"
    order.agent_id = data.agent_id

    # prevent duplicate delivery record
    existing = db.query(models.Delivery).filter(
        models.Delivery.order_id == data.order_id
    ).first()

    if not existing:
        delivery = models.Delivery(
            order_id=data.order_id,
            agent_id=data.agent_id,
            status="assigned"
        )
        db.add(delivery)

    db.commit()

    return {"message": "Assigned successfully"}


# ================= MY DELIVERIES =================
@router.get("/my")
def get_my_deliveries(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    deliveries = db.query(models.Delivery).filter(
        models.Delivery.agent_id == int(user["sub"])
    ).all()

    result = []

    for d in deliveries:
        order = d.order

        if not order:
            continue

        result.append({
            "id": order.id,
            "receiver": order.receiver,
            "phone": order.phone,
            "address": order.address,
            "weight": order.weight,
            "latitude": order.latitude,
            "longitude": order.longitude,
            "status": order.status
        })

    return result


# ================= MARK DELIVERED =================
@router.put("/{id}/delivered")
def mark_delivered(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    order = db.query(models.Order).filter(
        models.Order.id == id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # ❌ prevent wrong updates
    if order.status == "delivered":
        return {"message": "Already delivered"}

    # update order
    order.status = "delivered"

    delivery = db.query(models.Delivery).filter(
        models.Delivery.order_id == id
    ).first()

    if delivery:
        delivery.status = "delivered"

    db.commit()

    return {"message": "Delivered successfully"}