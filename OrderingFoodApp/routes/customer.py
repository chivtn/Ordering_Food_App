# customer.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from OrderingFoodApp.models import *
from OrderingFoodApp.dao import customer_service as dao
from datetime import datetime
from OrderingFoodApp.dao.cart_service import get_cart_items, group_items_by_restaurant

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

# Giao diện trang chủ
@customer_bp.route('/')
#@login_required
def index():
    # user = current_user nếu đã đăng nhập, còn không thì None
    user = current_user if current_user.is_authenticated else None

    # Lấy TẤT CẢ mã khuyến mãi còn hiệu lực (không giới hạn)
    current_time = datetime.now()
    promos = PromoCode.query.filter(
        PromoCode.start_date <= current_time,
        PromoCode.end_date >= current_time
    ).all()

    # Lấy TẤT CẢ nhà hàng có đơn hàng (không giới hạn)
    top_restaurants = (db.session.query(
        Restaurant,
        func.count(Order.id).label('order_count')
    ).outerjoin(Order, Order.restaurant_id == Restaurant.id)
     .filter(Restaurant.approval_status == RestaurantApprovalStatus.APPROVED)
     .group_by(Restaurant.id)
     .order_by(func.count(Order.id).desc())
     .all())

    # Lấy TẤT CẢ món ăn bán chạy (không giới hạn)
    top_menu_items = (db.session.query(
        MenuItem, Restaurant, func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem, OrderItem.menu_item_id == MenuItem.id)
     .join(Restaurant, Restaurant.id == MenuItem.restaurant_id)
     .group_by(MenuItem.id, Restaurant.id)
     .order_by(func.sum(OrderItem.quantity).desc())
     .all())

    # Chuyển đổi kết quả
    featured_items = []
    for mi, res, sold in top_menu_items:
        mi.restaurant = res
        mi.total_sold = sold or 0
        featured_items.append(mi)

    return render_template('customer/index.html',
                           user=user,
                           promos=promos,
                           top_restaurants=top_restaurants,
                           featured_items=featured_items)


@customer_bp.route('/restaurants_list')
def restaurants_list():
    search_query = request.args.get('search', '')
    search_type = request.args.get('search_type', 'restaurants')  # Mặc định là tìm nhà hàng
    category_id = request.args.get('category_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Xác định loại truy vấn
    if search_query:
        if search_type == 'dishes':
            # Tìm kiếm món ăn
            data = dao.get_menu_items_by_name(search_query, page, per_page)
            menu_items = data['menu_items']
        else:
            # Tìm kiếm NHÀ HÀNG THEO TÊN (sử dụng hàm mới)
            data = dao.get_restaurants_by_name(search_query, page, per_page)
            restaurants = data['restaurants']
    elif category_id:
        # Tìm theo danh mục (chỉ áp dụng cho nhà hàng)
        data = dao.get_restaurants_by_category(category_id, page, per_page)
        restaurants = data['restaurants']
        search_type = 'restaurants'  # Đảm bảo hiển thị đúng loại
    else:
        data = dao.get_all_restaurants(page, per_page)
        restaurants = data['restaurants']
        search_type = 'restaurants'  # Đảm bảo hiển thị đúng loại

    categories = MenuCategory.query.all()

    # total_pages = (data['total'] + per_page - 1) // per_page

    # THÊM KIỂM TRA KHI KHÔNG CÓ DỮ LIỆU
    if data['total'] == 0:
        total_pages = 0
    else:
        total_pages = (data['total'] + per_page - 1) // per_page

    # # Tính toán start_page và end_page
    # start_page = max(1, page - 2)
    # end_page = min(total_pages, page + 2)

    # Tính toán start_page và end_page CHỈ KHI CÓ TRANG
    if total_pages > 0:
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)

        # Điều chỉnh nếu khoảng trang < 5
        if end_page - start_page < 4:
            if start_page == 1:
                end_page = min(total_pages, start_page + 4)
            else:
                start_page = max(1, end_page - 4)
    else:
        start_page = end_page = 0

    # Nếu số trang ít hơn 5, điều chỉnh để hiển thị đủ
    if end_page - start_page < 4:
        if start_page == 1:
            end_page = min(total_pages, start_page + 4)
        else:
            start_page = max(1, end_page - 4)

    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': data['total'],
        'total_pages': total_pages,
        'start_page': start_page,
        'end_page': end_page
    }

    # Lấy danh sách mã khuyến mãi còn hiệu lực
    current_time = datetime.now()
    promos = PromoCode.query.filter(
        PromoCode.start_date <= current_time,
        PromoCode.end_date >= current_time
    ).limit(5).all()

    # Truyền dữ liệu phù hợp với loại tìm kiếm
    if search_type == 'dishes':
        return render_template('customer/restaurants_list.html',
                               menu_items=menu_items,
                               categories=categories,
                               search_query=search_query,
                               search_type=search_type,
                               selected_category_id=category_id,
                               pagination=pagination_info,
                               promos=promos)
    else:
        return render_template('customer/restaurants_list.html',
                               restaurants=restaurants,
                               categories=categories,
                               search_query=search_query,
                               search_type=search_type,
                               selected_category_id=category_id,
                               pagination=pagination_info,
                               promos=promos)


#Xem menu nhà hàng
def _is_open_now(opening: time, closing: time, now: time) -> bool:
    if not opening or not closing:
        return False
    # Hỗ trợ ca qua đêm: ví dụ 18:00 → 02:00
    if opening <= closing:
        return opening <= now < closing
    else:
        return now >= opening or now < closing

@customer_bp.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    now_local = datetime.now().time()  # hoặc dùng timezone nếu có
    open_now = _is_open_now(restaurant.opening_time, restaurant.closing_time, now_local)
    return render_template("customer/restaurant_detail.html",
                           restaurant=restaurant,
                           menu_items=menu_items,
                           open_now=open_now)


# Xem chi tiết món ăn
from sqlalchemy.orm import joinedload
@customer_bp.route("/menu_item/<int:menu_item_id>")
def view_menu_item(menu_item_id):
    # Eager load restaurant để tránh N+1
    menu_item = (MenuItem.query
                 .options(joinedload(MenuItem.restaurant))
                 .get_or_404(menu_item_id))

    now_local = datetime.now().time()  # nếu có timezone, chuyển sang tz địa phương
    open_now = _is_open_now(menu_item.restaurant.opening_time,
                            menu_item.restaurant.closing_time,
                            now_local)

    return render_template("customer/menu_item_detail.html",
                           menu_item=menu_item,
                           open_now=open_now)

# @customer_bp.route('/menu_item/<int:menu_item_id>')
# def view_menu_item(menu_item_id):
#     menu_item = MenuItem.query.get_or_404(menu_item_id)
#     return render_template('customer/menu_item_detail.html', menu_item=menu_item)


# Quản lý giỏ hàng
from OrderingFoodApp.dao import cart_service as cart_dao
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from OrderingFoodApp.models import MenuItem

@customer_bp.route('/cart', methods=['GET', 'POST'])
def cart():
    """
    - GET: render giỏ hàng (group theo nhà hàng)
    - POST:
        + AJAX: increase/decrease/remove -> trả về JSON {quantity, subtotal}
        + Form thường (add/decrease/remove) -> cập nhật rồi redirect /customer/cart
    - Khi user đã đăng nhập, mọi thay đổi đều được đồng bộ xuống DB (do cart_dao.update_cart làm sẵn)
    """
    cart_dao.init_cart()  # đảm bảo có session['cart']

    if request.method == 'POST':
        action  = request.form.get('action')           # add | increase | decrease | remove
        item_id = request.form.get('item_id')          # id món (str/int)
        qty     = request.form.get('quantity', type=int, default=1)

        if not item_id:
            return redirect(url_for('customer.cart'))

        # ----- AJAX -----
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            new_cart = cart_dao.update_cart(action, item_id, qty)
            menu_item = MenuItem.query.get(int(item_id))
            quantity  = int(new_cart.get(str(item_id), 0))
            subtotal  = float(menu_item.price) * quantity if menu_item else 0.0
            return jsonify({'quantity': quantity, 'subtotal': subtotal})

        # ----- Submit form thường -----
        cart_dao.update_cart(action, item_id, qty)
        return redirect(url_for('customer.cart'))

    # ----- GET -> render -----
    items, total_price = cart_dao.get_cart_items()
    grouped_items      = cart_dao.group_items_by_restaurant(items)
    return render_template('customer/cart.html',
                           grouped_items=grouped_items,
                           total_price=total_price)



# @customer_bp.route('/orders')
# @login_required
# def orders_history():
#     # Chỉ lấy đơn hàng của người dùng hiện tại (current_user.id)
#     orders = dao.get_orders_history(current_user.id)
#
#     # --- Prefetch review của chính user cho các đơn đang hiển thị ---
#     order_ids = [o.id for o in orders]
#     if order_ids:
#         reviews = (Review.query
#                    .filter(Review.customer_id == current_user.id,
#                            Review.order_id.in_(order_ids))
#                    .all())
#         r_by_order = {r.order_id: r for r in reviews}
#         for o in orders:
#             o.user_review = r_by_order.get(o.id)  # None nếu chưa có
#
#     return render_template('customer/orders_history.html', orders=orders)

@customer_bp.route('/orders')
@login_required
def orders_history():
    orders = dao.get_orders_history(current_user.id)

    # gom review của user cho các order trên
    order_ids = [o.id for o in orders]
    reviews = Review.query.filter(
        Review.customer_id == current_user.id,
        Review.order_id.in_(order_ids)
    ).all()
    reviews_map = {r.order_id: r for r in reviews}
    for o in orders:
        o.user_review = reviews_map.get(o.id)

    return render_template('customer/orders_history.html',
                           orders=orders,
                           reviews_map=reviews_map)


from OrderingFoodApp.dao import order_review_service as dao_order_review

@customer_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    # Lấy chi tiết đơn hàng và kiểm tra xem đơn hàng có thuộc về người dùng hiện tại không
    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first_or_404()

    # Lấy các món trong đơn hàng
    order_items = (OrderItem.query
                   .filter_by(order_id=order_id)
                   .join(MenuItem)
                   .all())

    # Lấy thông tin thanh toán nếu có
    payment = Payment.query.filter_by(order_id=order_id).first()

    # NEW: dữ liệu review
    order_review = dao_order_review.get_order_review(current_user.id, order_id)
    can_review, reason, _ = dao_order_review.can_review_order(current_user.id, order_id)

    return render_template('customer/orders_history_detail.html',
                           order=order,
                           order_items=order_items,
                           payment=payment,
                           order_review=order_review,
                           can_review=can_review,
                           cannot_reason=reason)

@customer_bp.route('/order/<int:order_id>/review', methods=['POST'])
@login_required
def submit_order_review(order_id):
    rating  = request.form.get('rating', type=int)
    comment = request.form.get('comment', '', type=str)

    ok, msg = dao_order_review.upsert_order_review(current_user.id, order_id, rating, comment)

    # Hỗ trợ cả AJAX & form thường
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': ok, 'message': msg}), (200 if ok else 400)

    flash(msg, 'success' if ok else 'warning')
    return redirect(url_for('customer.order_detail', order_id=order_id))


@customer_bp.route('/restaurant/<int:restaurant_id>/reviews')
def restaurant_reviews(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    reviews = restaurant.reviews  # tất cả reviews đã load sẵn quan hệ ORM
    return render_template('customer/restaurant_reviews.html',
                           restaurant=restaurant,
                           reviews=reviews)


#Đặt hàng
@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items, total_price = get_cart_items()

    selected_ids = request.args.get('selected_ids') or request.form.get('selected_ids')
    if selected_ids:
        chosen = set(map(int, selected_ids.split(',')))
        items = [i for i in items if i['id'] in chosen]
        total_price = sum(i['subtotal'] for i in items)

    if not items:
        flash('Giỏ hàng trống hoặc chưa chọn món.', 'warning')
        return redirect(url_for('customer.cart'))

    # LƯU DẠNG PHẲNG (flat)
    session['checkout_data'] = {
        'items': items,
        'total_price': float(total_price)
    }
    session.modified = True

    return render_template('customer/checkout.html',
                           items=items,
                           total_price=total_price)



@customer_bp.route('/place_order', methods=['POST'])
@login_required
def place_order():
    try:
        data = request.get_json(silent=True) or {}
        payment_method_value = data.get('payment_method', 'cash_on_delivery')
        applied_promo        = data.get('applied_promo')  # {'code': '...', 'final_amount': ...}
        payment_method = PaymentMethod(payment_method_value)

        checkout_data = session.get('checkout_data') or {}
        if not checkout_data:
            return jsonify({'success': False, 'message': 'Không có dữ liệu thanh toán.'}), 400

        # ƯU TIÊN items (flat). Fallback: flatten từ grouped_items nếu còn session cũ
        items = checkout_data.get('items') or []
        if not items and checkout_data.get('grouped_items'):
            items = []
            for pack in checkout_data['grouped_items'].values():
                sub = pack.get('items') if isinstance(pack, dict) else pack
                if sub: items.extend(sub)

        total_amount = float(checkout_data.get('total_price', 0))

        unique_restaurant_ids = set()
        all_items_flat = []   # [(MenuItem, qty)]
        for it in items:
            mi = MenuItem.query.get(int(it['id']))
            if not mi:
                return jsonify({'success': False, 'message': 'Món ăn không còn tồn tại.'}), 400
            unique_restaurant_ids.add(mi.restaurant_id)
            qty = int(it.get('quantity', 1))
            all_items_flat.append((mi, qty))

        if not all_items_flat:
            return jsonify({'success': False, 'message': 'Giỏ hàng trống.'}), 400
        if len(unique_restaurant_ids) != 1:
            return jsonify({'success': False, 'message': 'Chỉ được đặt món từ một nhà hàng trong một đơn.'}), 400

        restaurant_id = unique_restaurant_ids.pop()

        # Áp mã giảm giá nếu có
        promo_id = None
        if applied_promo and applied_promo.get('code'):
            promo = PromoCode.query.filter_by(code=applied_promo['code']).first()
            if promo:
                promo_id = promo.id
                total_amount = float(applied_promo.get('final_amount', total_amount))

        # Tạo Order + Items + Payment
        new_order = Order(
            customer_id=current_user.id,
            restaurant_id=restaurant_id,
            promo_code_id=promo_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        db.session.add(new_order)
        db.session.flush()

        for mi, qty in all_items_flat:
            db.session.add(OrderItem(
                order_id=new_order.id,
                menu_item_id=mi.id,
                quantity=qty,
                price=mi.price
            ))

        db.session.add(Payment(
            order_id=new_order.id,
            amount=total_amount,
            method=payment_method,
            status=PaymentStatus.PENDING
        ))

        # Xoá các món đã đặt khỏi giỏ (session) và commit
        session_cart = session.get('cart', {})
        for mi, _ in all_items_flat:
            session_cart.pop(str(mi.id), None)
        session['cart'] = session_cart
        session.pop('checkout_data', None)
        db.session.commit()

        # Đồng bộ giỏ DB theo session
        cart_dao._sync_db_from_session()

        # Thông báo
        db.session.add(Notification(
            user_id=current_user.id,
            order_id=new_order.id,
            type=NotificationType.ORDER_STATUS,
            message=f"Đơn hàng #{new_order.id} đã được đặt thành công.",
            is_read=False
        ))
        db.session.commit()

        return jsonify({
            'success': True,
            'order_id': new_order.id,
            'message': 'Đặt hàng thành công!',
            'redirect_url': url_for('customer.current_orders')
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {e}'}), 500



@customer_bp.route('/current_orders')
@login_required
def current_orders():
    # Lấy các đơn hàng chưa hoàn thành của khách hàng hiện tại
    orders = Order.query.filter(
        Order.customer_id == current_user.id,
        Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING])
    ).options(
        db.joinedload(Order.restaurant),
        db.joinedload(Order.order_items).joinedload(OrderItem.menu_item)
    ).order_by(Order.created_at.desc()).all()

    # Tạo dictionary để lưu trữ chi tiết từng đơn hàng
    orders_details = {}
    status_colors = {
        OrderStatus.PENDING: 'bg-warning text-dark',
        OrderStatus.CONFIRMED: 'bg-info text-white',
        OrderStatus.PREPARING: 'bg-primary text-white',
        OrderStatus.COMPLETED: 'bg-success text-white',
        OrderStatus.CANCELLED: 'bg-danger text-white'
    }

    for order in orders:
        # Lấy các món trong đơn hàng
        order_items = OrderItem.query.filter_by(order_id=order.id).join(MenuItem).all()

        # Lấy thông tin thanh toán nếu có
        payment = Payment.query.filter_by(order_id=order.id).first()

        orders_details[order.id] = {
            'order': order,
            'order_items': order_items,
            'payment': payment,
            'status_color': status_colors.get(order.status, 'bg-secondary')
        }

    return render_template('customer/current_orders.html',
                           orders=orders,
                           orders_details=orders_details,
                           PaymentStatus=PaymentStatus,
                           OrderStatus=OrderStatus,
                           DiscountType=DiscountType)


@customer_bp.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    try:
        order = Order.query.filter_by(
            id=order_id,
            customer_id=current_user.id,
            status=OrderStatus.PENDING
        ).first_or_404()

        order.status = OrderStatus.CANCELLED
        db.session.commit()

        # Tạo thông báo
        notification = Notification(
            user_id=current_user.id,
            order_id=order.id,
            type=NotificationType.ORDER_STATUS,
            message=f"Đơn hàng #{order.id} đã được hủy.",
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Đã hủy đơn hàng thành công'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Có lỗi xảy ra: {str(e)}'
        }), 500


@customer_bp.route('/promo_codes')
@login_required
def get_promo_codes():
    try:
        current_time = datetime.now()
        promos = PromoCode.query.filter(
            PromoCode.start_date <= current_time,
            PromoCode.end_date >= current_time
        ).all()

        promos_data = []
        for promo in promos:
            promos_data.append({
                'id': promo.id,
                'code': promo.code,
                'description': promo.description,
                'discount_type': promo.discount_type.value,
                'discount_value': float(promo.discount_value),
                'start_date': promo.start_date.isoformat(),
                'end_date': promo.end_date.isoformat(),
                'usage_limit': promo.usage_limit,
                'image_url': promo.image_url
            })

        return jsonify({'promos': promos_data})

    except Exception as e:
        app.logger.error(f'Lỗi khi lấy mã giảm giá: {str(e)}')
        return jsonify({'promos': [], 'error': str(e)}), 500


@customer_bp.route('/apply_promo', methods=['POST'])
@login_required
def apply_promo():
    data = request.get_json()
    promo_code = data.get('promo_code')
    total_price = float(data.get('total_price', 0))

    # Tìm mã giảm giá
    promo = PromoCode.query.filter_by(code=promo_code).first()
    if not promo:
        return jsonify({'success': False, 'message': 'Mã giảm giá không tồn tại'}), 400

    current_time = datetime.now()
    if current_time < promo.start_date or current_time > promo.end_date:
        return jsonify({'success': False, 'message': 'Mã giảm giá đã hết hạn'}), 400

    # Tính toán số tiền giảm
    # CHUYỂN ĐỔI Decimal SANG FLOAT TRƯỚC KHI TÍNH TOÁN
    discount_value = float(promo.discount_value)

    if promo.discount_type == DiscountType.PERCENT:
        discount_amount = total_price * (discount_value / 100)
    else:  # FIXED
        discount_amount = discount_value

    # Đảm bảo không giảm quá tổng tiền
    if discount_amount > total_price:
        discount_amount = total_price

    final_amount = total_price - discount_amount

    return jsonify({
        'success': True,
        'message': 'Áp dụng mã giảm giá thành công',
        'discount_amount': discount_amount,
        'final_amount': final_amount
    })