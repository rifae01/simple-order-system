# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description, "price": self.price}

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="placed")
    payment_status = db.Column(db.String(50), default="pending")

    order_items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def total_amount(self):
        return sum([oi.quantity * oi.unit_price for oi in self.order_items])

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "payment_status": self.payment_status,
            "items": [oi.to_dict() for oi in self.order_items],
            "total": self.total_amount()
        }

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", back_populates="order_items")
    item = db.relationship("Item")

    def to_dict(self):
        return {
            "id": self.id,
            "item": {"id": self.item.id, "name": self.item.name},
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "subtotal": self.unit_price * self.quantity
        }
