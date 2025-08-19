# OrderingFoodApp/config.py
import os

class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")  # nhớ đổi trên production

    # Database (cho phép override bằng ENV)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:askme@localhost/db_orderingfood?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ===== MoMo (sandbox) =====
    MOMO_PARTNER_CODE = os.getenv("MOMO_PARTNER_CODE", "MOMOXXXX2020")
    MOMO_ACCESS_KEY   = os.getenv("MOMO_ACCESS_KEY",   "F8BBA842ECF85")
    MOMO_SECRET_KEY   = os.getenv("MOMO_SECRET_KEY",   "K951B6PE1waDMi640xX08PD3vg6EkVlz")
    MOMO_ENDPOINT     = os.getenv("MOMO_ENDPOINT", "https://test-payment.momo.vn/v2/gateway/api/create")
    EXTERNAL_BASE_URL = os.getenv("EXTERNAL_BASE_URL")
    MOMO_QUERY_ENDPOINT = os.getenv("MOMO_QUERY_ENDPOINT", "https://test-payment.momo.vn/v2/gateway/api/query")

    # ===== VNPay (sandbox) =====
    VNP_TMN_CODE   = os.getenv("VNP_TMN_CODE",   "XXXXXXXX")
    VNP_HASH_SECRET= os.getenv("VNP_HASH_SECRET","YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
    VNP_API_URL    = os.getenv("VNP_API_URL",    "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
    # Lưu ý: nhớ đổi domain thật khi deploy
    VNP_RETURN_URL = os.getenv("VNP_RETURN_URL", "http://localhost:5000/payment/vnpay_return")
    VNP_IPN_URL = os.getenv("VNP_IPN_URL", "http://localhost:5000/payment/vnpay_ipn")

