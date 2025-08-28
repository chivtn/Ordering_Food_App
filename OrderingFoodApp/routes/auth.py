#auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from OrderingFoodApp import oauth
from OrderingFoodApp.models import db, User, UserRole
from urllib.parse import urlparse, urljoin

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

def _is_safe_url(target):
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target or ''))
    return (test.scheme in ('http', 'https') and ref.netloc == test.netloc)


# Đăng ký tài khoản
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name')
        email    = request.form.get('email')
        password = request.form.get('password')
        role     = request.form.get('role')  # 'CUSTOMER' | 'OWNER' | 'ADMIN'

        if User.query.filter_by(email=email).first():
            flash('Email này đã được đăng ký!', 'danger')
            return redirect(url_for('auth.register', next=request.args.get('next')))

        hashed_pw = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_pw, role=UserRole[role])
        db.session.add(user)
        db.session.commit()
        flash('Đăng ký thành công! Hãy đăng nhập.', 'success')

        next_page = request.args.get('next')
        # Chỉ chuyển tiếp `next` (checkout) nếu đăng ký khách hàng
        if role == 'CUSTOMER' and next_page and _is_safe_url(next_page):
            return redirect(url_for('auth.login', next=next_page))
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', next=request.args.get('next'))


from OrderingFoodApp.models import Cart, CartItem
from flask import session

# def _load_cart_from_db(user):
#     cart = {}
#     user_cart = Cart.query.filter_by(customer_id=user.id).first()
#     if user_cart:
#         for ci in user_cart.cart_items:
#             cart[str(ci.menu_item_id)] = ci.quantity
#     session['cart'] = cart
#     session.pop('checkout_data', None)

def _merge_guest_cart_to_db(user):
    """
    Hợp nhất giỏ trong session (guest) vào giỏ DB của user sau khi đăng nhập.
    Sau khi merge, nạp lại session['cart'] theo DB.
    """
    guest_cart = session.get('cart', {}) or {}        # {'menu_item_id(str)': qty(int)}
    # Tạo giỏ DB nếu chưa có
    user_cart = Cart.query.filter_by(customer_id=user.id).first()
    if not user_cart:
        user_cart = Cart(customer_id=user.id)
        db.session.add(user_cart)
        db.session.flush()

    # Lập map item_id -> CartItem
    existing = {str(ci.menu_item_id): ci for ci in user_cart.cart_items}

    # Gộp: cộng dồn số lượng
    for item_id_str, qty in guest_cart.items():
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            qty = 0
        if qty <= 0:
            continue

        if item_id_str in existing:
            existing[item_id_str].quantity += qty
        else:
            db.session.add(CartItem(
                cart_id=user_cart.id,
                menu_item_id=int(item_id_str),
                quantity=qty
            ))

    db.session.commit()

    # Nạp lại session theo DB sau merge (làm chuẩn)
    new_session_cart = {}
    for ci in user_cart.cart_items:
        if ci.quantity > 0:
            new_session_cart[str(ci.menu_item_id)] = int(ci.quantity)

    session['cart'] = new_session_cart
    session.pop('checkout_data', None)


# Đăng nhập
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        next_qs   = request.args.get('next')
        next_form = request.form.get('next')
        next_page = next_form or next_qs

        if user and check_password_hash(user.password, password):
            login_user(user)
            _merge_guest_cart_to_db(user)

            # CHỈ khách hàng mới được quay lại checkout
            if user.role == UserRole.CUSTOMER and next_page and _is_safe_url(next_page):
                return redirect(next_page)

            # Còn lại: về trang theo vai trò
            if user.role == UserRole.CUSTOMER:
                return redirect(url_for('customer.index'))
            elif user.role == UserRole.OWNER:
                return redirect(url_for('owner.index'))
            else:
                return redirect(url_for('admin.index'))
        else:
            flash('Email hoặc mật khẩu không đúng.', 'danger')

    # giữ lại next để form login có thể truyền lại (hidden input hoặc action)
    return render_template('auth/login.html', next=request.args.get('next'))



# Đăng xuất
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    # Sau khi thoát tài khoản: giỏ guest trống (theo đúng mong muốn)
    session['cart'] = {}
    session.pop('checkout_data', None)
    return redirect(url_for('customer.index'))

# ======= Google Login =======
from OrderingFoodApp.models import User, db, UserRole
from authlib.integrations.flask_client import OAuth
from flask import current_app

# Route login Google
# ======= Google Login =======
@auth_bp.route('/login/google')
def login_google():
    google = oauth.create_client('google')
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/google/callback')
def google_callback():
    # Lấy access token
    token = oauth.google.fetch_access_token(
        authorization_response=request.url,
        redirect_uri=url_for("auth.google_callback", _external=True)
    )

    # Gọi API lấy thông tin user
    resp = oauth.google.get("https://www.googleapis.com/oauth2/v2/userinfo", token=token)
    user_info = resp.json()

    email = user_info.get("email")
    name = user_info.get("name", email.split("@")[0])

    user = User.query.filter_by(email=email).first()
    if user:
        # User đã tồn tại -> login luôn
        login_user(user)
        _merge_guest_cart_to_db(user)
        flash("Đăng nhập Google thành công!", "success")
        return redirect(url_for("customer.index"))
    else:
        # User chưa tồn tại -> lưu tạm thông tin vào session
        session["google_user_info"] = {"email": email, "name": name}
        return redirect(url_for("auth.register_google"))

@auth_bp.route('/register_google', methods=["GET", "POST"])
def register_google():
    google_info = session.get("google_user_info")
    if not google_info:
        flash("Phiên đăng ký Google không hợp lệ, vui lòng thử lại.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        # Lấy dữ liệu từ form
        phone = request.form.get("phone")
        address = request.form.get("address")

        # Tạo user mới
        new_user = User(
            name=google_info["name"],
            email=google_info["email"],
            phone=phone,
            role=UserRole.CUSTOMER
        )
        db.session.add(new_user)
        db.session.commit()

        # Login luôn sau khi đăng ký
        login_user(new_user)
        session.pop("google_user_info", None)  # Xóa session tạm
        flash("Đăng ký tài khoản Google thành công!", "success")
        return redirect(url_for("customer.index"))

    return render_template("auth/register_google.html", google_info=google_info)
