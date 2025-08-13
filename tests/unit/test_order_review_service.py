import pytest
from OrderingFoodApp import db
from OrderingFoodApp.models import Review, OrderStatus
from OrderingFoodApp.dao import order_review_service as srv


@pytest.mark.usefixtures("app", "seed_review_data")
def test_can_review_order_completed(app):
    ok, msg, order = srv.can_review_order(customer_id=10, order_id=1001)
    assert ok is True
    assert order is not None
    assert order.status == OrderStatus.COMPLETED


@pytest.mark.usefixtures("app", "seed_review_data")
def test_can_review_order_not_completed(app):
    ok, msg, order = srv.can_review_order(customer_id=10, order_id=1002)
    assert ok is False
    assert "hoàn thành" in msg.lower()


@pytest.mark.usefixtures("app", "seed_review_data")
def test_upsert_review_create_then_update(app):
    # Create
    ok, msg = srv.upsert_order_review(10, 1001, rating=5, comment="Rất tốt")
    assert ok is True

    rv = Review.query.filter_by(customer_id=10, order_id=1001).first()
    assert rv is not None
    assert rv.rating == 5
    assert rv.comment == "Rất tốt"
    assert rv.restaurant_id == 101  # auto gắn theo đơn

    # Update
    ok2, msg2 = srv.upsert_order_review(10, 1001, rating=4, comment="Ổn")
    assert ok2 is True

    rv = Review.query.filter_by(customer_id=10, order_id=1001).first()
    assert rv.rating == 4
    assert rv.comment == "Ổn"


@pytest.mark.usefixtures("app", "seed_review_data")
def test_upsert_review_invalid_rating(app):
    ok, msg = srv.upsert_order_review(10, 1001, rating=0, comment="bad")
    assert ok is False
    assert "1 đến 5" in msg
