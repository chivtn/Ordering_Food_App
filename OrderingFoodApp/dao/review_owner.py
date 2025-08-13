# OrderingFoodApp/dao/review_owner.py
from sqlalchemy import desc
from OrderingFoodApp import db
from OrderingFoodApp.models import (
    Review, ReviewResponse, Restaurant, User, Notification, NotificationType
)

class dao_review_owner:
    @staticmethod
    def list_reviews_of_owner(owner_id: int, page: int = 1, per_page: int = 10, only_unanswered: bool = False):
        q = db.session.query(Review).join(Restaurant, Review.restaurant_id == Restaurant.id)\
            .filter(Restaurant.owner_id == owner_id).order_by(desc(Review.created_at))
        if only_unanswered:
            q = q.outerjoin(ReviewResponse, ReviewResponse.review_id == Review.id)\
                 .filter(ReviewResponse.id.is_(None))
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_review_detail(owner_id: int, review_id: int) -> Review | None:
        r = db.session.query(Review).join(Restaurant, Review.restaurant_id == Restaurant.id)\
            .filter(Review.id == review_id, Restaurant.owner_id == owner_id).first()
        return r

    @staticmethod
    def upsert_response(owner_id: int, review_id: int, response_text: str):
        review = db.session.query(Review).join(Restaurant, Review.restaurant_id == Restaurant.id)\
            .filter(Review.id == review_id, Restaurant.owner_id == owner_id).first()
        if not review:
            return False, "Không tìm thấy đánh giá hoặc bạn không có quyền."

        response = ReviewResponse.query.filter_by(review_id=review_id, owner_id=owner_id).first()
        if response:
            response.response_text = (response_text or "").strip()
        else:
            response = ReviewResponse(review_id=review_id, owner_id=owner_id,
                                      response_text=(response_text or "").strip())
            db.session.add(response)

        # Gửi notification cho khách hàng
        msg = f"Chủ nhà hàng đã phản hồi đánh giá cho đơn #{review.order_id}."
        noti = Notification(user_id=review.customer_id,
                            order_id=review.order_id,
                            type=NotificationType.REVIEW_RESPONSE,
                            message=msg)
        db.session.add(noti)

        db.session.commit()
        return True, "Đã lưu phản hồi."

    @staticmethod
    def delete_response(owner_id: int, review_id: int):
        resp = ReviewResponse.query.filter_by(review_id=review_id, owner_id=owner_id).first()
        if not resp:
            return False, "Không có phản hồi để xóa."
        db.session.delete(resp)
        db.session.commit()
        return True, "Đã xóa phản hồi."
