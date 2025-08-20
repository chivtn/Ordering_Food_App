# tests/unit/test_payments.py
import time
import urllib.parse
from datetime import datetime, timedelta

import pytest
from flask import url_for

from OrderingFoodApp import db
from OrderingFoodApp.models import (
    User, UserRole, Restaurant, MenuCategory, MenuItem,
    Order, OrderItem, Payment, PaymentMethod, PaymentStatus, OrderStatus
)
# Import đúng các helper ký chữ ký đã viết trong module payment.py
from OrderingFoodApp.routes.payment import (
    _momo_build_raw_from_params_for_verify,
    _momo_sign,
    _vnp_hash_for_verify,
)

@pytest.fixture
def seed_order_for_payments(app):
    """Seed: 1 owner, 1 customer(id=10), 1 restaurant, 1 item, 1 order + payment(PENDING)"""
    with app.app_context():
        owner = User(id=1, name="Owner", email="owner@test.local",
                     password="x", role=UserRole.OWNER)
        customer = User(id=10, name="Cus", email="cus@test.local",
                        password="x", role=UserRole.CUSTOMER)
        rest = Restaurant(id=1, owner_id=1, name="R1", address="", phone="")
        cat = MenuCategory(id=1, name="Cat", image_url=None)
        item = MenuItem(id=1, restaurant_id=1, category_id=1,
                        name="M1", description="", price=50000)

        db.session.add_all([owner, customer, rest, cat, item])
        db.session.flush()

        order = Order(
            id=100,
            customer_id=10,
            restaurant_id=1,
            total_amount=50000,     # 50,000 VND
            status=OrderStatus.PENDING,
        )
        db.session.add(order)
        db.session.flush()

        db.session.add(OrderItem(order_id=order.id, menu_item_id=item.id,
                                 quantity=1, price=item.price))

        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            method=PaymentMethod.CASH_ON_DELIVERY,  # method không ảnh hưởng test
            status=PaymentStatus.PENDING,
        )
        db.session.add(payment)
        db.session.commit()


# ---------- MoMo ----------
def test_momo_return_success(client, app, seed_order_for_payments, login_customer):
    """
    Giả lập redirect return từ MoMo (resultCode=0). Ký chữ ký đúng -> 302 redirect,
    và Payment chuyển COMPLETED.
    """
    with app.app_context():
        # Tham số return từ MoMo
        base_id = "100"
        orderId = f"{base_id}-{int(time.time())}"
        requestId = f"{base_id}-{int(time.time())}"
        params = {
            "amount": 50000,
            "extraData": "",
            "message": "Successful.",
            "orderId": orderId,
            "orderInfo": f"Thanh toan don hang #{base_id}",
            "orderType": "momo_wallet",
            "partnerCode": app.config["MOMO_PARTNER_CODE"],
            "payType": "wallet",
            "requestId": requestId,
            "responseTime": int(time.time() * 1000),
            "resultCode": 0,
            "transId": 123456789
        }

        # Tính chữ ký như server
        raw = _momo_build_raw_from_params_for_verify(params, app.config["MOMO_ACCESS_KEY"])
        sig = _momo_sign(raw, app.config["MOMO_SECRET_KEY"])
        params["signature"] = sig

        # Gọi endpoint
        url = url_for("customer.momo_return", **params)
        res = client.get(url, follow_redirects=False)
        assert res.status_code in (302, 303)

        # Kiểm tra Payment chuyển COMPLETED
        p = Payment.query.filter_by(order_id=100).first()
        assert p is not None
        assert p.status == PaymentStatus.COMPLETED


def test_momo_ipn_success(client, app, seed_order_for_payments):
    """
    Giả lập IPN từ MoMo (resultCode=0). Ký chữ ký đúng -> 200 JSON,
    Payment chuyển COMPLETED.
    """
    with app.app_context():
        base_id = "100"
        orderId = f"{base_id}-{int(time.time())}"
        requestId = f"{base_id}-{int(time.time())}"
        body = {
            "amount": 50000,
            "extraData": "",
            "message": "Successful.",
            "orderId": orderId,
            "orderInfo": f"Thanh toan don hang #{base_id}",
            "orderType": "momo_wallet",
            "partnerCode": app.config["MOMO_PARTNER_CODE"],
            "payType": "wallet",
            "requestId": requestId,
            "responseTime": int(time.time() * 1000),
            "resultCode": 0,
            "transId": 987654321
        }

        raw = _momo_build_raw_from_params_for_verify(dict(body), app.config["MOMO_ACCESS_KEY"])
        body["signature"] = _momo_sign(raw, app.config["MOMO_SECRET_KEY"])

        res = client.post(url_for("customer.momo_ipn"), json=body)
        assert res.status_code == 200
        # payload success {resultCode: 0, ...}
        assert res.is_json
        assert res.get_json().get("resultCode") == 0

        p = Payment.query.filter_by(order_id=100).first()
        assert p.status == PaymentStatus.COMPLETED


# ---------- VNPay ----------
def test_vnpay_payment_redirect_url(client, app, seed_order_for_payments, login_customer):
    """
    Gọi /payment/vnpay/<order_id> -> 302 sang VNPay sandbox URL,
    có đủ tham số và có vnp_SecureHash.
    """
    with app.app_context():
        res = client.get(url_for("customer.vnpay_payment", order_id=100), follow_redirects=False)
        assert res.status_code in (302, 303)
        loc = res.headers.get("Location", "")
        assert loc.startswith(app.config["VNP_API_URL"])
        # Có tham số ký
        qs = urllib.parse.urlparse(loc).query
        parsed = dict(urllib.parse.parse_qsl(qs))
        assert "vnp_SecureHash" in parsed
        assert parsed.get("vnp_TmnCode") == app.config["VNP_TMN_CODE"]


def test_vnpay_return_success(client, app, seed_order_for_payments, login_customer):
    """
    Giả lập redirect return từ VNPay (vnp_ResponseCode=00) với chữ ký hợp lệ,
    Payment chuyển COMPLETED.
    """
    with app.app_context():
        base_id = "100"
        txn_ref = f"{base_id}-{int(time.time())}"
        now = datetime.now()

        params = {
            "vnp_Version": "2.1.0",
            "vnp_TmnCode": app.config["VNP_TMN_CODE"],
            "vnp_Amount": 50000 * 100,   # đơn vị x100
            "vnp_Command": "pay",
            "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
            "vnp_CurrCode": "VND",
            "vnp_IpAddr": "127.0.0.1",
            "vnp_Locale": "vn",
            "vnp_OrderInfo": f"Thanh toan don hang #{base_id}",
            "vnp_OrderType": "billpayment",
            "vnp_ReturnUrl": app.config["VNP_RETURN_URL"],
            "vnp_TxnRef": txn_ref,
            "vnp_ExpireDate": (now + timedelta(minutes=15)).strftime("%Y%m%d%H%M%S"),
            "vnp_ResponseCode": "00",  # thành công
        }

        # Tính chữ ký cho VERIFY (server-side)
        sig = _vnp_hash_for_verify(dict(params), app.config["VNP_HASH_SECRET"])
        params["vnp_SecureHash"] = sig
        params["vnp_SecureHashType"] = "HMACSHA512"

        res = client.get(url_for("customer.vnpay_return", **params), follow_redirects=False)
        assert res.status_code in (302, 303)

        p = Payment.query.filter_by(order_id=100).first()
        assert p is not None
        assert p.status == PaymentStatus.COMPLETED
