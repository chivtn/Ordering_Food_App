# tests/conftest.py

import os
import pytest
from flask import Flask

from OrderingFoodApp import init_app, db
from flask import session
from OrderingFoodApp.models import *

@pytest.fixture(scope='session')
def app():
    # Cho biết ta đang ở môi trường test
    os.environ['FLASK_ENV'] = 'testing'

    # Tạo app từ init_app
    app: Flask = init_app()
    app.config.update({
        'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:askme@127.0.0.1:3306/test_db',
    'WTF_CSRF_ENABLED': False,
    'SECRET_KEY': 'test-secret',

    # --- Thêm các key cho MoMo & VNPay (dùng giá trị mock khi test) ---
    'MOMO_PARTNER_CODE': 'MOMOTEST',
    'MOMO_ACCESS_KEY':   'TESTACCESS',
    'MOMO_SECRET_KEY':   'TESTSECRET',
    'MOMO_ENDPOINT':     'https://example-momo/create',   # placeholder, test không gọi thật
    'MOMO_QUERY_ENDPOINT': 'https://example-momo/query',

    'VNP_TMN_CODE':    'TMNCODE',
    'VNP_HASH_SECRET': 'VNPSECRET',
    'VNP_API_URL':     'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
    'VNP_RETURN_URL':  'http://localhost/payment/vnpay_return',
    })

    # Tạo toàn bộ bảng
    with app.app_context():
        db.create_all()

    yield app

    # Sau cùng drop bảng
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_db(app):
    # Trước mỗi test truncate hết các bảng
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

@pytest.fixture
def login_customer(client):
    """
    Đăng nhập giả bằng cách set _user_id trong session (Flask-Login).
    Trả về id của user đã login.
    """
    with client.session_transaction() as s:
        # sẽ tạo user ở seed; ở đây chỉ set khi đã có user 10
        s["_user_id"] = "10"
        s["_fresh"] = True
    return 10


@pytest.fixture
def seed_review_data(app):
    """
    Tạo dữ liệu tối thiểu cho review:
    - owner (id=1) để gán owner nhà hàng
    - customer (id=10) để đăng nhập/đánh giá
    - restaurant (id=101)
    - order COMPLETED (id=1001) thuộc về customer 10
    - order PENDING   (id=1002) thuộc về customer 10
    """
    from OrderingFoodApp.models import Payment, PaymentMethod, PaymentStatus

    with app.app_context():
        owner = User(id=1, name="Owner", email="o@x.com", password="p", role=UserRole.OWNER)
        customer = User(id=10, name="Cus", email="c@x.com", password="p", role=UserRole.CUSTOMER)
        r = Restaurant(id=101, owner_id=1, name="R", address="", phone="")
        # COMPLETED
        o1 = Order(
            id=1001, customer_id=10, restaurant_id=101,
            total_amount=100000, status=OrderStatus.COMPLETED
        )
        # PENDING
        o2 = Order(
            id=1002, customer_id=10, restaurant_id=101,
            total_amount=200000, status=OrderStatus.PENDING
        )
        db.session.add_all([owner, customer, r, o1, o2])
        db.session.commit()