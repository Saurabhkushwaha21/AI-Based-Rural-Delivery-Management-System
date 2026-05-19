from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float,Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False)
    role = Column(String(20), default="user")
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(200), nullable=True)

    # 👇 specify foreign key explicitly
    orders = relationship(
        "Order",
        foreign_keys="Order.user_id",
        back_populates="user"
    )

    deliveries = relationship(
        "Delivery",
        foreign_keys="Delivery.agent_id",
        back_populates="agent"
    )

class Hub(Base):
    __tablename__ = "hubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    orders = relationship("Order", back_populates="hub")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    hub_id = Column(Integer, ForeignKey("hubs.id"))

    receiver = Column(String(100))
    phone = Column(String(20))
    package_type = Column(String(100))
    weight = Column(Float)
    address = Column(String(200))

    latitude = Column(Float)
    longitude = Column(Float)

    status = Column(String(50), default="pending")

    # 👇 FIX HERE
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="orders"
    )

    agent = relationship(   # optional but recommended
        "User",
        foreign_keys=[agent_id]
    )

    hub = relationship("Hub", back_populates="orders")
    delivery = relationship("Delivery", back_populates="order", uselist=False)


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"))
    agent_id = Column(Integer, ForeignKey("users.id"))

    cluster_id = Column(Integer)
    status = Column(String(50), default="assigned")

    order = relationship("Order", back_populates="delivery")

    agent = relationship(
        "User",
        foreign_keys=[agent_id],
        back_populates="deliveries"
    )


class AgentLocation(Base):
    __tablename__ = "agent_locations"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("users.id"))

    latitude = Column(Float)
    longitude = Column(Float)

    current_order_id = Column(Integer, nullable=True)
    status = Column(String(20), default="idle")  

    updated_at = Column(DateTime, default=datetime.now(timezone.utc))    