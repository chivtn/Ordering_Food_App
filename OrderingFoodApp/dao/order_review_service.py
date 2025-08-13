# dao/order_review_service.py
from OrderingFoodApp import db
from OrderingFoodApp.models import Order, OrderStatus, Review

def can_review_order(customer_id: int, order_id: int) -> tuple[bool, str | None, Order | None]:
    """
    Quyền review: đơn phải thuộc về customer_id, và status == COMPLETED.
    """
    order = Order.query.filter_by(id=order_id, customer_id=customer_id).first()
    if not order:
        return False, "Đơn hàng không tồn tại hoặc không thuộc về bạn.", None
    if order.status != OrderStatus.COMPLETED:
        return False, "Chỉ có thể đánh giá khi đơn hàng đã hoàn thành.", order
    return True, None, order

def get_order_review(customer_id: int, order_id: int) -> Review | None:
    return Review.query.filter_by(customer_id=customer_id, order_id=order_id).first()

def upsert_order_review(customer_id: int, order_id: int, rating: int, comment: str | None):
    if rating is None or rating < 1 or rating > 5:
        return False, "Điểm đánh giá phải từ 1 đến 5."

    ok, msg, order = can_review_order(customer_id, order_id)
    if not ok:
        return False, msg

    existing = get_order_review(customer_id, order_id)
    if existing:
        existing.rating = rating
        existing.comment = (comment or "").strip()
        db.session.commit()
        return True, "Đã cập nhật đánh giá đơn hàng."
    else:
        rv = Review(
            customer_id=customer_id,
            restaurant_id=order.restaurant_id,
            order_id=order.id,                 # CHÚ Ý: gắn theo đơn để đảm bảo uniqueness
            rating=rating,
            comment=(comment or "").strip()
        )
        db.session.add(rv)
        db.session.commit()
        return True, "Đã gửi đánh giá đơn hàng."
