#cart_service.py
from flask import session
from flask_login import current_user
from OrderingFoodApp.models import db, MenuItem, Cart, CartItem

def _ensure_user_cart(user_id):
    cart = Cart.query.filter_by(customer_id=user_id).first()
    if not cart:
        cart = Cart(customer_id=user_id)
        db.session.add(cart)
        db.session.flush()
    return cart

def _sync_db_from_session():
    """Đồng bộ giỏ từ session xuống DB cho user đã đăng nhập."""
    if not current_user.is_authenticated:
        return
    cart_dict = session.get('cart', {})
    cart = _ensure_user_cart(current_user.id)

    # Tạo map hiện tại của DB
    db_items = {str(ci.menu_item_id): ci for ci in cart.cart_items}

    # Upsert theo session
    for mid, qty in cart_dict.items():
        if qty <= 0:
            continue
        if mid in db_items:
            db_items[mid].quantity = qty
        else:
            db.session.add(CartItem(cart_id=cart.id, menu_item_id=int(mid), quantity=qty))

    # Xóa những món không còn trong session
    for mid, row in list(db_items.items()):
        if mid not in cart_dict:
            db.session.delete(row)

    db.session.commit()

def init_cart():
    """Khởi tạo giỏ hàng nếu chưa có"""
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']


# cart_service.py
from flask_login import current_user
from OrderingFoodApp.models import db, Cart, CartItem

def update_cart(action, item_id, quantity=None):
    cart = init_cart()
    item_id = str(item_id)

    if action == 'add':
        current_quantity = cart.get(item_id, 0)
        cart[item_id] = current_quantity + (quantity or 1)
    elif action == 'increase':
        cart[item_id] = cart.get(item_id, 0) + 1
    elif action == 'decrease':
        if cart.get(item_id, 0) > 1:
            cart[item_id] -= 1
        else:
            cart.pop(item_id, None)
    elif action == 'remove':
        cart.pop(item_id, None)

    session['cart'] = cart

    # Đồng bộ DB nếu đã đăng nhập
    if current_user.is_authenticated:
        user_cart = Cart.query.filter_by(customer_id=current_user.id).first()
        if not user_cart:
            user_cart = Cart(customer_id=current_user.id)
            db.session.add(user_cart)
            db.session.flush()

        # Map hiện tại trong DB
        db_items = {str(ci.menu_item_id): ci for ci in user_cart.cart_items}

        # Cập nhật/ thêm
        for mid, qty in cart.items():
            ci = db_items.get(mid)
            if ci:
                ci.quantity = qty
            else:
                db.session.add(CartItem(cart=user_cart, menu_item_id=int(mid), quantity=qty))

        # Xóa những món không còn trong session
        for mid, ci in list(db_items.items()):
            if mid not in cart:
                db.session.delete(ci)

        db.session.commit()

    return cart



def get_cart_items():
    """Luôn đọc theo session (đã được đồng bộ lúc login/ thao tác)"""
    cart = init_cart()
    items, total_price = [], 0
    for item_id, quantity in cart.items():
        menu_item = MenuItem.query.get(int(item_id))
        if not menu_item:
            continue
        subtotal = float(menu_item.price) * quantity
        total_price += subtotal
        items.append({
            'id': menu_item.id,
            'name': menu_item.name,
            'price': float(menu_item.price),
            'quantity': quantity,
            'subtotal': subtotal,
            'restaurant_name': menu_item.restaurant.name,
            'image_url': menu_item.image_url
        })
    return items, total_price


# def group_items_by_restaurant(items):
#     """Nhóm món theo nhà hàng"""
#     grouped = {}
#     for item in items:
#         grouped.setdefault(item['restaurant_name'], []).append(item)
#     return grouped

def group_items_by_restaurant(items):
    grouped = {}
    for it in items:
        id = it.get('restaurant_id') if 'restaurant_id' in it else MenuItem.query.get(it['id']).restaurant_id
        name = it.get('restaurant_name')
        bucket = grouped.setdefault(id, {'name': name, 'items': []})
        bucket['items'].append(it)
    return grouped

