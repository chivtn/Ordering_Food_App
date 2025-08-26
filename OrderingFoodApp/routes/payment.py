#payment.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from flask_login import login_required, current_user
from OrderingFoodApp.models import *
from datetime import datetime, timedelta
import hmac, hashlib, requests, json
import urllib.parse
import time
from urllib.parse import urljoin


from OrderingFoodApp.routes.customer import customer_bp

#Thanh toán
#MOMO
def _momo_sign(raw_string: str, secret_key: str) -> str:
    return hmac.new(secret_key.encode('utf-8'), raw_string.encode('utf-8'), hashlib.sha256).hexdigest()

# --- momo_payment ---
@customer_bp.route('/payment/momo/<int:order_id>')
@login_required
def momo_payment(order_id):
    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first_or_404()

    # (tùy chọn) nếu đã hoàn tất payment thì thôi
    payment = Payment.query.filter_by(order_id=order.id).first()
    if payment and payment.status == PaymentStatus.COMPLETED:
        flash("Đơn hàng đã thanh toán.", "info")
        return redirect(url_for('customer.order_complete', order_id=order.id))

    # Tạo orderId/requestId unique như bạn đã sửa
    base_id     = str(order.id)
    orderId     = f"{base_id}-{int(time.time())}"
    requestId   = f"{base_id}-{int(time.time())}"
    amount_int  = int(order.total_amount)

    # ►► DEMO OFFLINE
    if current_app.config.get('MOMO_OFFLINE_DEMO'):
        # (nếu đã thêm cột momo_order_id/request_id thì lưu lại)
        if payment:
            try:
                payment.momo_order_id   = orderId
                payment.momo_request_id = requestId
                db.session.commit()
            except Exception:
                db.session.rollback()
        return redirect(url_for('customer.momo_fake_checkout',
                                order_id=order.id, orderId=orderId,
                                requestId=requestId, amount=amount_int))

    # ►► BÌNH THƯỜNG: gọi MoMo thật (đoạn bạn đã có sẵn)
    endpoint    = current_app.config['MOMO_ENDPOINT']
    partnerCode = current_app.config['MOMO_PARTNER_CODE'].strip()
    accessKey   = current_app.config['MOMO_ACCESS_KEY'].strip()
    secretKey   = current_app.config['MOMO_SECRET_KEY'].strip()


    base = current_app.config.get("EXTERNAL_BASE_URL")
    if base:
        redirectUrl = urljoin(base, url_for('customer.momo_return', _external=False))
        ipnUrl = urljoin(base, url_for('customer.momo_ipn', _external=False))
    else:
        redirectUrl = url_for('customer.momo_return', _external=True)
        ipnUrl = url_for('customer.momo_ipn', _external=True)

    requestType = "captureWallet"
    extraData   = ""

    raw = (
        f"accessKey={accessKey}"
        f"&amount={amount_int}"
        f"&extraData={extraData}"
        f"&ipnUrl={ipnUrl}"
        f"&orderId={orderId}"
        f"&orderInfo=Thanh toan don hang #{base_id}"
        f"&partnerCode={partnerCode}"
        f"&redirectUrl={redirectUrl}"
        f"&requestId={requestId}"
        f"&requestType={requestType}"
    )
    signature = _momo_sign(raw, secretKey)

    payload = {
        "partnerCode": partnerCode,
        "accessKey": accessKey,
        "requestId": requestId,
        "amount": str(amount_int),
        "orderId": orderId,
        "orderInfo": f"Thanh toan don hang #{base_id}",
        "redirectUrl": redirectUrl,
        "ipnUrl": ipnUrl,
        "extraData": extraData,
        "requestType": requestType,
        "signature": signature,
        "lang": "vi"
    }

    current_app.logger.info("MOMO RAW: %s", raw)
    current_app.logger.info("MOMO PAYLOAD: %s", payload)

    res = requests.post(endpoint, json=payload, timeout=60)
    data = res.json()
    if data.get("resultCode") != 0:
        current_app.logger.error("MoMo create failed: %s", data)
        flash(f"Lỗi tạo thanh toán MoMo: {data.get('message', data)}", "danger")
        return redirect(url_for('customer.order_complete', order_id=order.id))

    pay_url = data.get("payUrl") or data.get("deeplink") or data.get("qrCodeUrl")
    if not pay_url:
        current_app.logger.error("MoMo create missing payUrl: %s", data)
        flash("MoMo không trả về payUrl.", "danger")
        return redirect(url_for('customer.order_complete', order_id=order.id))

    return redirect(pay_url)

@customer_bp.route('/payment/momo_atm/<int:order_id>')
@login_required
def momo_payment_atm(order_id):
    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first_or_404()
    payment = Payment.query.filter_by(order_id=order.id).first()

    if payment and payment.status == PaymentStatus.COMPLETED:
        flash("Đơn hàng đã thanh toán.", "info")
        return redirect(url_for('customer.order_complete', order_id=order.id))

    endpoint    = current_app.config['MOMO_ENDPOINT']
    partnerCode = current_app.config['MOMO_PARTNER_CODE'].strip()
    accessKey   = current_app.config['MOMO_ACCESS_KEY'].strip()
    secretKey   = current_app.config['MOMO_SECRET_KEY'].strip()

    base_id   = str(order.id)
    ts        = int(time.time())
    orderId   = f"{base_id}-{ts}"
    requestId = f"{base_id}-{ts}"
    amount    = int(order.total_amount)
    extraData = ""
    orderInfo = f"Thanh toan don hang #{base_id}"

    base = (current_app.config.get("EXTERNAL_BASE_URL") or "").strip()
    if base:
        redirectUrl = urljoin(base, url_for('customer.momo_return', _external=False))
        ipnUrl      = urljoin(base, url_for('customer.momo_ipn', _external=False))
    else:
        redirectUrl = url_for('customer.momo_return', _external=True)
        ipnUrl      = url_for('customer.momo_ipn', _external=True)

    requestType = "payWithATM"

    # TÙY CHỌN: nếu cần ngân hàng sandbox, set mã tại đây. Nếu không thì để None.
    bankCode = None  # ví dụ: "SML" nếu bên bạn yêu cầu

    # === CHUỖI KÝ PHẢI TRÙNG ĐÚNG CÁC KEY GỬI LÊN (theo log MoMo) ===
    raw = (
        f"accessKey={accessKey}"
        f"&amount={amount}"
        f"&extraData={extraData}"
        f"&ipnUrl={ipnUrl}"
        f"&orderId={orderId}"
        f"&orderInfo={orderInfo}"
        f"&partnerCode={partnerCode}"
        f"&redirectUrl={redirectUrl}"
        f"&requestId={requestId}"
        f"&requestType={requestType}"
    )
    if bankCode:
        raw += f"&bankCode={bankCode}"

    signature = _momo_sign(raw, secretKey)

    payload = {
        "partnerCode": partnerCode,
        "accessKey": accessKey,
        "requestId": requestId,
        "amount": str(amount),
        "orderId": orderId,
        "orderInfo": orderInfo,
        "redirectUrl": redirectUrl,
        "ipnUrl": ipnUrl,
        "extraData": extraData,
        "requestType": requestType,
        "signature": signature,
        "lang": "vi",
    }
    if bankCode:
        payload["bankCode"] = bankCode

    current_app.logger.info("MOMO ATM RAW: %s", raw)
    current_app.logger.info("MOMO ATM PAYLOAD: %s", payload)

    try:
        res = requests.post(endpoint, json=payload, timeout=60)
        # NEW: log thô để biết MoMo trả gì
        current_app.logger.info("MOMO ATM RESP STATUS=%s", res.status_code)
        current_app.logger.info("MOMO ATM RESP TEXT=%s", res.text)

        try:
            data = res.json()
        except Exception:
            current_app.logger.error("MOMO ATM JSON decode error. Text=%s", res.text)
            flash("MoMo trả về dữ liệu không hợp lệ.", "danger")
            return redirect(url_for('customer.order_complete', order_id=order.id))

        data = res.json()
    except Exception as e:
        current_app.logger.exception("MoMo ATM request error: %s", e)
        flash("Không gọi được cổng MoMo (ATM).", "danger")
        return redirect(url_for('customer.order_complete', order_id=order.id))

    if str(data.get("resultCode")) != "0":
        current_app.logger.error("MoMo ATM create failed: %s", data)
        flash(f"Lỗi tạo thanh toán MoMo ATM: {data.get('message', data)}", "danger")
        return redirect(url_for('customer.order_complete', order_id=order.id))

    pay_url = (
        data.get("payUrl")
        or data.get("deeplink")
        or data.get("deeplinkUrl")
        or data.get("shortLink")
        or data.get("qrCodeUrl")
    )
    if not pay_url:
        current_app.logger.error("MoMo ATM missing payUrl: %s", data)
        flash("MoMo không trả về đường dẫn thanh toán ATM.", "danger")
        return redirect(url_for('customer.order_complete', order_id=order.id))

    return redirect(pay_url)


#verify
def _momo_build_raw_from_params_for_verify(p: dict, access_key: str) -> str:
    # Thứ tự CHUẨN của MoMo cho redirect/IPN (AIO v2)
    order = [
        "amount", "extraData", "message", "orderId", "orderInfo",
        "orderType", "partnerCode", "payType", "requestId",
        "responseTime", "resultCode", "transId",
    ]
    parts = [f"accessKey={access_key}"]
    for k in order:
        if k in p:  # giữ nguyên giá trị như MoMo gửi (int/str đều được, sẽ str() bên dưới)
            parts.append(f"{k}={p[k]}")
    return "&".join(parts)


def _verify_momo_signature(params: dict, signature: str) -> bool:
    secret_key = current_app.config['MOMO_SECRET_KEY']
    access_key = current_app.config['MOMO_ACCESS_KEY']

    raw = _momo_build_raw_from_params_for_verify(params, access_key)
    my_sig = _momo_sign(raw, secret_key)
    return hmac.compare_digest(my_sig, signature or "")

# --- momo_return ---
PENDING_CODES = {"99", "9000", "1006", "7002"}   # tuỳ tài liệu môi trường test

@customer_bp.route('/payment/momo_return')
def momo_return():
    params = dict(request.args.items())
    sig = params.pop("signature", None)
    if not _verify_momo_signature(params, sig):
        flash("Chữ ký MoMo không hợp lệ", "danger")
        return redirect(url_for("customer.current_orders"))

    rc           = str(params.get("resultCode"))
    raw_order_id = params.get("orderId", "")
    req_id       = params.get("requestId", "")

    base_id = raw_order_id.split("-")[0] if raw_order_id else None
    if not base_id:
        flash("Thiếu orderId từ MoMo.", "warning")
        return redirect(url_for("customer.current_orders"))

    order = Order.query.get_or_404(base_id)
    payment = Payment.query.filter_by(order_id=order.id).first()
    if not payment:
        flash("Không tìm thấy payment cho đơn hàng", "danger")
        return redirect(url_for("customer.current_orders"))

    # 1) Thành công chắc chắn
    if rc == "0":
        if payment.status != PaymentStatus.COMPLETED:
            payment.status = PaymentStatus.COMPLETED
            payment.paid_at = datetime.utcnow()
            db.session.commit()
        flash("Thanh toán MoMo thành công! Đơn hàng đang chờ nhà hàng xác nhận.", "success")
        return redirect(url_for("customer.order_complete", order_id=order.id))

    # 2) Đang xử lý -> thử Query 1 lần (KHÔNG dùng payment.momo_*)
    if rc in PENDING_CODES:
        if req_id:
            q = momo_query_txn(raw_order_id, req_id)
            current_app.logger.info("MOMO QUERY (on return) rc=%s -> %s", rc, q)

            if str(q.get("resultCode")) == "0":
                payment.status = PaymentStatus.COMPLETED
                payment.paid_at = datetime.utcnow()
                db.session.commit()
                flash("Thanh toán MoMo thành công!", "success")
                return redirect(url_for("customer.order_complete", order_id=order.id))

        # Giữ PENDING để chờ IPN chốt (không set FAILED ở đây)
        if payment.status != PaymentStatus.COMPLETED:
            payment.status = PaymentStatus.PENDING
            db.session.commit()
        flash("Giao dịch MoMo đang được xử lý. Hệ thống sẽ tự cập nhật khi có kết quả cuối.", "info")
        return redirect(url_for("customer.order_complete", order_id=order.id))

    # 3) Các mã khác -> coi như thất bại (trừ khi đã completed)
    if payment.status != PaymentStatus.COMPLETED:
        payment.status = PaymentStatus.FAILED
        db.session.commit()
    flash("Thanh toán MoMo thất bại.", "warning")
    return redirect(url_for("customer.order_complete", order_id=order.id))



# --- momo_ipn ---
@customer_bp.route('/payment/momo_ipn', methods=['POST'])
def momo_ipn():
    """
    Nhận IPN từ MoMo. Hỗ trợ cả JSON và form-url-encoded.
    Trả HTTP 200 trong mọi trường hợp để tránh MoMo retry quá nhiều.
    """

    # Log thô để dễ soi khi lệch chữ ký
    ctype = (request.headers.get('Content-Type') or '').lower()
    body_text = request.get_data(as_text=True)  # raw body chuỗi
    current_app.logger.info("MOMO IPN ctype=%s body=%s", ctype, body_text)

    # 1) Thử đọc JSON
    data = request.get_json(silent=True)

    # 2) Nếu không phải JSON, đọc form (application/x-www-form-urlencoded)
    if not data or not isinstance(data, dict):
        data = request.form.to_dict(flat=True)

    # 3) Trường hợp hiếm: provider gửi body kiểu querystring nhưng Flask chưa parse
    if not data and body_text:
        try:
            from urllib.parse import parse_qs
            data = {k: v[0] for k, v in parse_qs(body_text).items()}
        except Exception:
            data = {}

    # Sao lưu để log, rồi pop signature ra khỏi bộ tham số trước khi build raw
    recv_sig = (data or {}).get("signature")
    params_for_verify = dict(data or {})
    params_for_verify.pop("signature", None)

    # Build raw y hệt logic verify của bạn + tính chữ ký cục bộ
    try:
        access_key = current_app.config['MOMO_ACCESS_KEY']
        secret_key = current_app.config['MOMO_SECRET_KEY']
        raw = _momo_build_raw_from_params_for_verify(params_for_verify, access_key)
        calc_sig = _momo_sign(raw, secret_key)

        current_app.logger.info("MOMO IPN RAW: %s", raw)
        current_app.logger.info("MOMO IPN SIG(client): %s", recv_sig)
        current_app.logger.info("MOMO IPN SIG(server): %s", calc_sig)
    except Exception as e:
        current_app.logger.exception("MOMO IPN build-signature error: %s", e)
        # vẫn trả 200 để MoMo không retry
        return jsonify({"resultCode": 1001, "message": "Build signature error"}), 200

    # Verify chữ ký
    if not hmac.compare_digest(calc_sig, recv_sig or ""):
        current_app.logger.warning("MOMO IPN invalid signature. data=%s", data)
        # Trả 200 để MoMo không retry dồn; bạn giữ log để tự điều tra
        return jsonify({"resultCode": 1001, "message": "Invalid signature"}), 200

    # ---- Đến đây: chữ ký hợp lệ ----
    raw_order_id = (data.get("orderId") or "")
    base_id = raw_order_id.split("-")[0] if raw_order_id else None
    result_code = str(data.get("resultCode"))

    if not base_id:
        return jsonify({"resultCode": 1004, "message": "Missing orderId"}), 200

    order = Order.query.get(base_id)
    if not order:
        return jsonify({"resultCode": 1002, "message": "Order not found"}), 200

    payment = Payment.query.filter_by(order_id=order.id).first()
    if not payment:
        return jsonify({"resultCode": 1003, "message": "Payment not found"}), 200

    # Idempotent
    if payment.status == PaymentStatus.COMPLETED:
        return jsonify({"resultCode": 0, "message": "Order already updated"}), 200

    if result_code == "0":
        payment.status = PaymentStatus.COMPLETED
        payment.paid_at = datetime.utcnow()
    elif result_code in PENDING_CODES:
        # không đổi trạng thái, giữ PENDING
        pass
    else:
        payment.status = PaymentStatus.FAILED

    db.session.commit()
    return jsonify({"resultCode": 0, "message": "Confirm Success"}), 200


def momo_query_txn(orderId: str, requestId: str) -> dict:
    endpoint    = current_app.config['MOMO_QUERY_ENDPOINT']
    partnerCode = current_app.config['MOMO_PARTNER_CODE'].strip()
    accessKey   = current_app.config['MOMO_ACCESS_KEY'].strip()
    secretKey   = current_app.config['MOMO_SECRET_KEY'].strip()

    raw = (
        f"accessKey={accessKey}"
        f"&orderId={orderId}"
        f"&partnerCode={partnerCode}"
        f"&requestId={requestId}"
    )
    signature = _momo_sign(raw, secretKey)
    payload = {
        "partnerCode": partnerCode,
        "accessKey": accessKey,
        "requestId": requestId,
        "orderId": orderId,
        "signature": signature,
        "lang": "vi",
    }
    r = requests.post(endpoint, json=payload, timeout=30)
    try:
        return r.json()
    except Exception:
        return {"error": f"bad_response {r.status_code}", "text": r.text}


#======================VNPAY======================
import urllib.parse, hmac, hashlib

def _vnp_hash_for_request(params: dict, secret: str) -> str:
    data = {k: v for k, v in params.items()
            if k not in ("vnp_SecureHash", "vnp_SecureHashType")}
    # encode theo đúng cách bạn dùng để build URL (quote_plus)
    enc = lambda s: urllib.parse.quote_plus(str(s), safe='')
    hash_data = "&".join(f"{enc(k)}={enc(v)}" for k, v in sorted(data.items()))
    return hmac.new(secret.encode("utf-8"),
                    hash_data.encode("utf-8"),
                    hashlib.sha512).hexdigest().upper()


def _vnp_hash_for_verify(params: dict, secret: str) -> str:
    data = {k: v for k, v in params.items()
            if k not in ("vnp_SecureHash", "vnp_SecureHashType")}
    enc = lambda s: urllib.parse.quote_plus(str(s), safe='')
    base = "&".join(f"{enc(k)}={enc(v)}" for k, v in sorted(data.items()))
    return hmac.new(secret.strip().encode("utf-8"),
                    base.encode("utf-8"),
                    hashlib.sha512).hexdigest().upper()


def _vnp_verify(query_params: dict) -> bool:
    secret = current_app.config['VNP_HASH_SECRET']
    data = dict(query_params)
    recv = (data.pop("vnp_SecureHash", "") or "").upper()
    data.pop("vnp_SecureHashType", None)
    calc = _vnp_hash_for_verify(data, secret)
    return bool(recv) and hmac.compare_digest(calc, recv)

@customer_bp.route('/payment/vnpay/<int:order_id>')
@login_required
def vnpay_payment(order_id):
    # 1) Lấy order TRƯỚC
    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first_or_404()

    # 2) Lấy cấu hình
    vnp_url    = current_app.config['VNP_API_URL']
    vnp_tmn    = current_app.config['VNP_TMN_CODE']
    vnp_secret = current_app.config['VNP_HASH_SECRET']

    # 3) Build return/ipn cùng host (EXTERNAL_BASE_URL nếu có, ngược lại host hiện tại)
    base = current_app.config.get("EXTERNAL_BASE_URL")
    if base:
        vnp_return = urljoin(base, url_for('customer.vnpay_return', _external=False))
        vnp_ipn    = urljoin(base, url_for('customer.vnpay_ipn', _external=False))
    else:
        vnp_return = url_for('customer.vnpay_return', _external=True)
        vnp_ipn    = url_for('customer.vnpay_ipn', _external=True)

    # 4) Tham số giao dịch
    now = datetime.now()
    expire = now + timedelta(minutes=15)
    txn_ref = f"{order.id}-{int(now.timestamp())}"

    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": vnp_tmn,
        "vnp_Amount": int(order.total_amount) * 100,
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": f"Thanh toan don hang #{order.id}",
        "vnp_OrderType": "billpayment",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": vnp_return,
        "vnp_IpAddr": request.headers.get('X-Forwarded-For', request.remote_addr or "127.0.0.1"),
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_ExpireDate": expire.strftime("%Y%m%d%H%M%S"),
        "vnp_SecureHashType": "HMACSHA512",
    }

    params["vnp_SecureHash"] = _vnp_hash_for_request(params, vnp_secret)
    query = urllib.parse.urlencode(params, doseq=True, safe='')
    pay_url = f"{vnp_url}?{query}"
    return redirect(pay_url)



@customer_bp.route('/payment/vnpay_return')
def vnpay_return():
    params = dict(request.args.items())
    if not _vnp_verify(params):
        flash("Chữ ký VNPay không hợp lệ", "danger")
        return redirect(url_for("customer.current_orders"))

    txn_ref  = params.get("vnp_TxnRef", "")
    base_id  = txn_ref.split("-")[0]
    resp_code = params.get("vnp_ResponseCode")

    order = Order.query.get_or_404(base_id)
    payment = Payment.query.filter_by(order_id=order.id).first()
    if not payment:
        flash("Không tìm thấy payment cho đơn hàng", "danger")
        return redirect(url_for("customer.current_orders"))

    if resp_code == "00":
        if payment.status != PaymentStatus.COMPLETED:
            payment.status = PaymentStatus.COMPLETED
            payment.paid_at = datetime.utcnow()
        # KHÔNG đổi order.status (đợi nhà hàng xác nhận)
        flash("Thanh toán VNPay thành công! Đơn hàng đang chờ nhà hàng xác nhận.", "success")
    else:
        if payment.status != PaymentStatus.FAILED:
            payment.status = PaymentStatus.FAILED
        flash("Thanh toán VNPay thất bại", "warning")

    db.session.commit()

    return redirect(url_for("customer.order_complete", order_id=order.id))


@customer_bp.route('/payment/vnpay_ipn')
def vnpay_ipn():
    params = dict(request.args.items())
    if not _vnp_verify(params):
        return jsonify({"RspCode": "97", "Message": "Invalid Signature"}), 200

    txn_ref   = params.get("vnp_TxnRef", "")
    base_id   = txn_ref.split("-")[0]
    amount    = int(params.get("vnp_Amount", "0") or 0)
    resp_code = params.get("vnp_ResponseCode")

    order   = Order.query.get(base_id)
    if not order:   return jsonify({"RspCode": "01", "Message": "Order not found"}), 200

    payment = Payment.query.filter_by(order_id=order.id).first()
    if not payment: return jsonify({"RspCode": "01", "Message": "Payment not found"}), 200

    if int(round(float(payment.amount) * 100)) != amount:
        return jsonify({"RspCode": "04", "Message": "Invalid amount"}), 200

    if payment.status == PaymentStatus.COMPLETED:
        return jsonify({"RspCode": "02", "Message": "Order already updated"}), 200

    if resp_code == "00":
        payment.status = PaymentStatus.COMPLETED
        payment.paid_at = datetime.utcnow()
    else:
        payment.status = PaymentStatus.FAILED

    db.session.commit()
    return jsonify({"RspCode": "00", "Message": "Confirm Success"}), 200

