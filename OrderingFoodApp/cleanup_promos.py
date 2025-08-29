# OrderingFoodApp/scripts/cleanup_promos.py
import os
import sys
from datetime import datetime, timezone

# Thêm đường dẫn gốc dự án để import được OrderingFoodApp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from OrderingFoodApp import init_app, db
from OrderingFoodApp.models import PromoCode  # giả sử bạn có model PromoCode

def cleanup_expired_promos():
    """Xóa mã giảm giá đã hết hạn"""
    app = init_app()
    with app.app_context():
        now = datetime.now(timezone.utc)

        # Tìm các mã giảm giá đã hết hạn
        expired_promos = PromoCode.query.filter(PromoCode.end_date < now).all()

        if expired_promos:
            for promo in expired_promos:
                db.session.delete(promo)
            db.session.commit()
            print(f"Đã xóa {len(expired_promos)} mã giảm giá hết hạn.")
        else:
            print("Không có mã giảm giá hết hạn.")

if __name__ == "__main__":
    cleanup_expired_promos()
