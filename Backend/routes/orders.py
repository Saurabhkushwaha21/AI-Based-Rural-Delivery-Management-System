from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schema
from dependencies import get_current_user, require_role
import requests
import math

router = APIRouter(tags=["Rural System"])

# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= DISTANCE =================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


def find_nearest_hub(lat, lon, hubs):

    nearest = None
    min_dist = float("inf")

    for hub in hubs:

        dist = haversine(
            lat,
            lon,
            hub.latitude,
            hub.longitude
        )

        if dist < min_dist:
            min_dist = dist
            nearest = hub

    return nearest

# ================= ML =================
def call_ml_service(locations):

    try:

        res = requests.post(
            "http://127.0.0.1:8001/cluster",
            json={
                "locations": locations,
                "k": 2
            },
            timeout=5
        )

        res.raise_for_status()

        return res.json()

    except requests.exceptions.RequestException:

        return {
            "error": "ML service unavailable"
        }

# ================= CREATE ORDER =================
# ================= ORDERS =================

@router.post("/create")
def create_order(
    order: schema.OrderCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    hubs = db.query(models.Hub).all()

    if not hubs:
        raise HTTPException(status_code=400, detail="No hubs available")

    nearest_hub = find_nearest_hub(
        order.latitude,
        order.longitude,
        hubs
    )

    new_order = models.Order(
        user_id=int(user["sub"]),
        receiver=order.receiver,
        phone=order.phone,
        package_type=order.package_type,
        weight=order.weight,
        address=order.address,
        latitude=order.latitude,
        longitude=order.longitude,
        status="pending",
        hub_id=nearest_hub.id
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order created",
        "order_id": new_order.id
    }


@router.get("/all")
def get_all_orders(
    db: Session = Depends(get_db)
):

    return db.query(models.Order).all()


@router.get("/my")
def get_my_orders(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(models.Order).filter(
        models.Order.user_id == int(user["sub"])
    ).all()


@router.get("/optimize-route")
def optimize_route(
    db: Session = Depends(get_db)
):

    orders = db.query(models.Order).filter(
        models.Order.status == "pending"
    ).all()

    locations = [
        {
            "lat": o.latitude,
            "lon": o.longitude,
            "order_id": o.id
        }
        for o in orders
    ]

    return call_ml_service(locations)

# ================= GET HUBS =================
@router.get("/hubs")
def get_hubs(
    db: Session = Depends(get_db)
):

    return db.query(models.Hub).all()

# ================= GET AGENTS =================
@router.get("/agents")
def get_agents(
    db: Session = Depends(get_db)
):

    return db.query(models.User).filter(
        models.User.role == "agent"
    ).all()

# ================= ADMIN DASHBOARD =================
@router.get("/dashboard/admin")
def admin_dashboard(
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):

    orders = db.query(models.Order).all()

    hubs = db.query(models.Hub).all()

    agents = db.query(models.User).filter(
        models.User.role == "agent"
    ).all()

    return {
        "total_orders": len(orders),
        "pending": len([
            o for o in orders
            if o.status.lower() == "pending"
        ]),
        "assigned": len([
            o for o in orders
            if o.status.lower() == "assigned"
        ]),
        "delivered": len([
            o for o in orders
            if o.status.lower() == "delivered"
        ]),
        "total_hubs": len(hubs),
        "total_agents": len(agents)
    }


# ================= AGENT DASHBOARD =================
@router.get("/dashboard/agent")
def agent_dashboard(
    user=Depends(require_role("agent")),
    db: Session = Depends(get_db)
):

    orders = db.query(models.Order).filter(
        models.Order.agent_id == int(user["sub"])
    ).all()

    assigned = len([
        o for o in orders
        if o.status.lower() == "assigned"
    ])

    delivered = len([
        o for o in orders
        if o.status.lower() == "delivered"
    ])

    total = len(orders)

    success_rate = 0

    if total > 0:
        success_rate = round(
            (delivered / total) * 100
        )

    return {
        "assigned": assigned,
        "delivered": delivered,
        "success_rate": f"{success_rate}%"
    }


# ================= USER DASHBOARD =================
@router.get("/dashboard/user")
def user_dashboard(
    user=Depends(require_role("user")),
    db: Session = Depends(get_db)
):

    orders = db.query(models.Order).filter(
        models.Order.user_id == int(user["sub"])
    ).all()

    total = len(orders)

    pending = len([
        o for o in orders
        if o.status.lower() == "pending"
    ])

    assigned = len([
        o for o in orders
        if o.status.lower() == "assigned"
    ])

    delivered = len([
        o for o in orders
        if o.status.lower() == "delivered"
    ])

    return {
        "total": total,
        "pending": pending,
        "assigned": assigned,
        "delivered": delivered,
        "orders": orders
    }