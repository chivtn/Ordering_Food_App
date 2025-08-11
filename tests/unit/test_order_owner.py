import pytest
from OrderingFoodApp.dao import order_owner as dao
from OrderingFoodApp.models import (
    db, User, Restaurant, Order, OrderItem, OrderStatus,
    RestaurantApprovalStatus, MenuCategory, MenuItem
)

@pytest.fixture
def seed_order_data(app):
    with app.app_context():
        # Tạo users
        owner = User(name="Owner", email="owner@test.com", password="pass", role="owner")
        customer = User(name="Customer", email="cust@test.com", password="pass", role="customer")
        db.session.add_all([owner, customer])
        db.session.commit()

        # Tạo restaurant
        rest = Restaurant(
            owner_id=owner.id,
            name="Test Restaurant",
            description="desc",
            address="addr",
            phone="123",
            approval_status=RestaurantApprovalStatus.APPROVED
        )
        db.session.add(rest)
        db.session.commit()

        # Tạo category
        category = MenuCategory(name="Test Category", image_url="test.jpg")
        db.session.add(category)
        db.session.commit()

        # Tạo menu item
        menu_item = MenuItem(
            restaurant_id=rest.id,
            category_id=category.id,
            name="Test Item",
            price=50000
        )
        db.session.add(menu_item)
        db.session.commit()

        # Tạo order
        order = Order(
            customer_id=customer.id,
            restaurant_id=rest.id,
            total_amount=100000,
            status=OrderStatus.PENDING
        )
        db.session.add(order)
        db.session.commit()

        # Tạo order item
        item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=2,
            price=50000
        )
        db.session.add(item)
        db.session.commit()

        return {
            "owner_id": owner.id,
            "customer_id": customer.id,
            "restaurant_id": rest.id,
            "order_id": order.id
        }

def test_get_orders_by_owner(app, seed_order_data):
    with app.app_context():
        data = dao.OrderDAO.get_orders_by_owner(owner_id=seed_order_data["owner_id"])
        assert data["total"] == 1
        assert data["orders"][0]["customer_name"] == \
               User.query.get(seed_order_data["customer_id"]).name

def test_update_order_status_success(app, seed_order_data):
    with app.app_context():
        oid = seed_order_data["order_id"]
        assert dao.OrderDAO.update_order_status(oid, "confirmed") is True
        assert Order.query.get(oid).status == OrderStatus.CONFIRMED

def test_update_order_status_invalid_flow(app, seed_order_data):
    with app.app_context():
        oid = seed_order_data["order_id"]
        assert dao.OrderDAO.update_order_status(oid, "preparing") is False

def test_get_order_details(app, seed_order_data):
    with app.app_context():
        oid = seed_order_data["order_id"]
        details = dao.OrderDAO.get_order_details(oid)
        assert details["id"] == oid
        assert details["customer"]["name"] == \
               User.query.get(seed_order_data["customer_id"]).name

def test_cancel_order_invalid_when_completed(app, seed_order_data):
    with app.app_context():
        oid = seed_order_data["order_id"]

        # Giả lập trạng thái đã hoàn thành
        order = Order.query.get(oid)
        order.status = OrderStatus.CONFIRMED
        # Thử hủy → phải False
        assert dao.OrderDAO.update_order_status(oid, "cancelled") is False
        assert Order.query.get(oid).status == OrderStatus.CONFIRMED