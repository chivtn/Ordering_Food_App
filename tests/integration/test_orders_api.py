import pytest
from flask_login import login_user
from OrderingFoodApp.models import db, User, Restaurant, Order, OrderStatus, RestaurantApprovalStatus

@pytest.fixture
def seed_integration_data(app):
    with app.app_context():
        owner = User(name="Owner", email="owner@test.com", password="pass", role="owner")
        customer = User(name="Customer", email="cust@test.com", password="pass", role="customer")
        db.session.add_all([owner, customer])
        db.session.commit()

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

        order = Order(
            customer_id=customer.id,
            restaurant_id=rest.id,
            total_amount=100000,
            status=OrderStatus.PENDING
        )
        db.session.add(order)
        db.session.commit()

        # Trả về ID thay vì object để tránh DetachedInstanceError
        return {
            "owner_id": owner.id,
            "customer_id": customer.id,
            "restaurant_id": rest.id,
            "order_id": order.id
        }

def login_as_owner(client, owner_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(owner_id)
        sess["_fresh"] = True

def test_owner_orders_page(client, seed_integration_data):
    login_as_owner(client, seed_integration_data["owner_id"])
    resp = client.get("/owner/orders")
    assert resp.status_code == 200
    assert b"Test Restaurant" in resp.data


def test_update_order_status_api(client, seed_integration_data):
    login_as_owner(client, seed_integration_data["owner_id"])
    resp = client.post(
        f"/owner/orders/{seed_integration_data['order_id']}/update-status",
        data={"status": "confirmed"}
    )
    json_data = resp.get_json()
    assert json_data["success"] is True
