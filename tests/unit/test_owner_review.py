# tests/unit/test_owner_review.py
import pytest
from OrderingFoodApp import db
from OrderingFoodApp.models import (
    User, Restaurant, Review, ReviewResponse,
    Order, OrderStatus
)
from OrderingFoodApp.dao.review_owner import dao_review_owner


@pytest.fixture
def seed_review(app):
    """Seed: 1 owner, 1 customer, 1 restaurant, 1 order (COMPLETED), 1 review"""
    with app.app_context():
        owner = User(id=1, name="Owner", email="o@x.com", password="p", role="owner")
        customer = User(id=2, name="Customer", email="c@x.com", password="p", role="customer")
        rest = Restaurant(id=1, owner_id=1, name="Nhà hàng A", address="", phone="")

        # PHẢI có Order để thỏa FK của Review.order_id
        order = Order(
            id=10,
            customer_id=2,
            restaurant_id=1,
            total_amount=100000,
            status=OrderStatus.COMPLETED
        )

        review = Review(
            id=1,
            order_id=10,
            restaurant_id=1,
            customer_id=2,
            rating=5,
            comment="Ngon lắm!"
        )

        db.session.add_all([owner, customer, rest, order, review])
        db.session.commit()
        yield  # cho test dùng dữ liệu này


def test_list_reviews(app, seed_review):
    with app.app_context():
        page = dao_review_owner.list_reviews_of_owner(owner_id=1, page=1, per_page=10)
        assert page.total == 1
        rv = page.items[0]
        assert rv.restaurant_id == 1
        assert rv.customer_id == 2
        assert rv.order_id == 10
        assert rv.rating == 5


def test_respond_review(app, seed_review):
    with app.app_context():
        ok, msg = dao_review_owner.upsert_response(owner_id=1, review_id=1, response_text="Cảm ơn bạn!")
        assert ok is True

        # đã tạo hoặc cập nhật ReviewResponse
        resp = ReviewResponse.query.filter_by(review_id=1, owner_id=1).first()
        assert resp is not None
        assert resp.response_text == "Cảm ơn bạn!"

        # gọi lần 2 -> update
        ok2, _ = dao_review_owner.upsert_response(owner_id=1, review_id=1, response_text="Đã ghi nhận!")
        assert ok2 is True
        resp2 = ReviewResponse.query.filter_by(review_id=1, owner_id=1).first()
        assert resp2.response_text == "Đã ghi nhận!"


def test_delete_response(app, seed_review):
    with app.app_context():
        # tạo trước 1 phản hồi
        ok, _ = dao_review_owner.upsert_response(owner_id=1, review_id=1, response_text="Cảm ơn!")
        assert ok is True

        # xóa phản hồi
        ok_del, msg_del = dao_review_owner.delete_response(owner_id=1, review_id=1)
        assert ok_del is True

        resp = ReviewResponse.query.filter_by(review_id=1, owner_id=1).first()
        assert resp is None
