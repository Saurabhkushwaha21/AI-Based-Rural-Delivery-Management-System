from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import requests
from datetime import datetime

router = APIRouter()

# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= ML SERVICE =================
def call_ml_service(locations):
    try:
        response = requests.post(
            "http://127.0.0.1:8001/cluster",
            json={"locations": locations, "k": 2},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"error": "ML service unavailable"}


def call_demand_service(history):
    try:
        response = requests.post(
            "http://127.0.0.1:8001/predict",
            json={"history": history},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"error": "Demand service unavailable"}


# ================= AUTO ASSIGN =================
@router.post("/auto-assign")
def auto_assign(db: Session = Depends(get_db)):

    # ✅ FIX: correct status
    orders = db.query(models.Order).filter(
        models.Order.status == "pending"
    ).all()

    agents = db.query(models.User).filter(
        models.User.role == "agent"
    ).all()

    if not orders:
        return {"message": "No pending orders"}

    if not agents:
        return {"message": "No agents available"}

    # prepare ML input
    locations = [
        {"lat": o.latitude, "lon": o.longitude, "order_id": o.id}
        for o in orders
    ]

    result = call_ml_service(locations)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    clusters = result.get("clusters", {})

    for cluster_id, cluster_orders in clusters.items():

        # ✅ FIX: balanced agent selection (least load)
        agent = min(agents, key=lambda a: len(a.deliveries))

        for loc in cluster_orders:

            # ✅ prevent duplicate delivery
            existing = db.query(models.Delivery).filter(
                models.Delivery.order_id == loc["order_id"]
            ).first()

            if existing:
                continue

            order = db.query(models.Order).filter(
                models.Order.id == loc["order_id"]
            ).first()

            if not order:
                continue

            # optional safety check
            if order.status != "pending":
                continue

            # create delivery
            delivery = models.Delivery(
                order_id=order.id,
                agent_id=agent.id,
                cluster_id=int(cluster_id)
            )
            db.add(delivery)

            # update order
            order.status = "assigned"

        db.commit()

    return {"message": "Orders clustered & assigned successfully"}


# ================= DEMAND PREDICTION =================
@router.post("/predict-demand")
def predict_demand_api(db: Session = Depends(get_db)):

    orders = db.query(models.Order).all()

    if not orders:
        return {"message": "No order history available"}

    # FIX: safe grouping
    history_map = {}

    for order in orders:
        if not order.created_at:
            continue

        day = order.created_at.date()
        history_map[day] = history_map.get(day, 0) + 1

    # FIX: ordered history (important for ML)
    sorted_history = sorted(history_map.items(), key=lambda x: x[0])

    history = [
        {"day": i + 1, "orders": count}
        for i, (_, count) in enumerate(sorted_history)
    ]

    result = call_demand_service(history)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result