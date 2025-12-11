# app.py
from flask import Flask, request, jsonify
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, Item, Order, OrderItem
import os

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)

    @app.route("/")
    def index():
        return jsonify({"message": "Simple Order System API"}), 200

    @app.route("/items", methods=["POST"])
    def add_item():
        data = request.get_json() or {}
        name = data.get("name")
        price = data.get("price")
        if not name or price is None:
            return jsonify({"error": "name and price required"}), 400
        item = Item(name=name, description=data.get("description"), price=float(price))
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201

    @app.route("/items", methods=["GET"])
    def list_items():
        items = Item.query.all()
        return jsonify([i.to_dict() for i in items]), 200

    @app.route("/items/<int:item_id>", methods=["PUT"])
    def update_item(item_id):
        item = Item.query.get_or_404(item_id)
        data = request.get_json() or {}
        item.name = data.get("name", item.name)
        item.description = data.get("description", item.description)
        if data.get("price") is not None:
            item.price = float(data.get("price"))
        db.session.commit()
        return jsonify(item.to_dict()), 200

    @app.route("/items/<int:item_id>", methods=["DELETE"])
    def delete_item(item_id):
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "deleted"}), 200

    @app.route("/orders", methods=["POST"])
    def place_order():
        data = request.get_json() or {}
        customer_name = data.get("customer_name")
        items = data.get("items", [])
        if not customer_name or not items:
            return jsonify({"error": "customer_name and items required"}), 400

        order = Order(customer_name=customer_name)
        db.session.add(order)
        db.session.flush()

        for it in items:
            item_obj = Item.query.get(it["item_id"])
            if not item_obj:
                db.session.rollback()
                return jsonify({"error": f"item {it['item_id']} not found"}), 404
            qty = int(it.get("quantity", 1))
            oi = OrderItem(order_id=order.id, item_id=item_obj.id, quantity=qty, unit_price=item_obj.price)
            db.session.add(oi)

        db.session.commit()
        return jsonify(order.to_dict()), 201

    @app.route("/orders/<int:order_id>", methods=["GET"])
    def get_order(order_id):
        order = Order.query.get_or_404(order_id)
        return jsonify(order.to_dict()), 200

    @app.route("/orders", methods=["GET"])
    def list_orders():
        customer = request.args.get("customer")
        q = Order.query
        if customer:
            q = q.filter(Order.customer_name.ilike(f"%{customer}%"))
        orders = q.order_by(Order.created_at.desc()).all()
        return jsonify([o.to_dict() for o in orders]), 200

    @app.route("/orders/<int:order_id>/payment", methods=["PUT"])
    def update_payment(order_id):
        order = Order.query.get_or_404(order_id)
        data = request.get_json() or {}
        status = data.get("payment_status")
        if status not in ("pending", "paid", "failed"):
            return jsonify({"error": "invalid payment_status"}), 400
        order.payment_status = status
        db.session.commit()
        return jsonify(order.to_dict()), 200

    @app.route("/orders/<int:order_id>/status", methods=["PUT"])
    def update_order_status(order_id):
        order = Order.query.get_or_404(order_id)
        data = request.get_json() or {}
        status = data.get("status")
        if status not in ("placed", "preparing", "delivered", "cancelled"):
            return jsonify({"error": "invalid status"}), 400
        order.status = status
        db.session.commit()
        return jsonify(order.to_dict()), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
