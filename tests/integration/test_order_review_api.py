import pytest
from OrderingFoodApp.models import Review


@pytest.mark.usefixtures("seed_review_data")
def test_submit_review_ajax_success(client, login_customer):
    # gửi AJAX để tạo review cho order COMPLETED
    r = client.post(
        "/customer/order/1001/review",
        data={"rating": 5, "comment": "Tuyệt vời"},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    assert r.status_code == 200
    j = r.get_json()
    assert j["success"] is True

    # đã tạo trong DB
    rv = Review.query.filter_by(customer_id=10, order_id=1001).first()
    assert rv and rv.rating == 5


@pytest.mark.usefixtures("seed_review_data")
def test_submit_review_ajax_invalid_rating(client, login_customer):
    r = client.post(
        "/customer/order/1001/review",
        data={"rating": 0, "comment": "x"},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    assert r.status_code == 400
    j = r.get_json()
    assert j["success"] is False


@pytest.mark.usefixtures("seed_review_data")
def test_submit_review_form_update(client, login_customer, app):
    # tạo trước 1 review
    with app.app_context():
        from OrderingFoodApp import db
        from OrderingFoodApp.models import Review
        db.session.add(Review(customer_id=10, restaurant_id=101, order_id=1001, rating=3, comment="ok"))
        db.session.commit()

    # gửi FORM thường (không AJAX) để update
    r = client.post(
        "/customer/order/1001/review",
        data={"rating": 4, "comment": "đã tốt hơn"},
        follow_redirects=False,
    )
    # route redirect về order_detail
    assert r.status_code in (302, 303)

    with app.app_context():
        rv = Review.query.filter_by(customer_id=10, order_id=1001).first()
        assert rv.rating == 4
        assert rv.comment == "đã tốt hơn"
