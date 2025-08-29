# customer_service.py
from sqlalchemy import func
from OrderingFoodApp.models import *
from OrderingFoodApp import db
from flask import request
from datetime import datetime
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt

from OrderingFoodApp.routes import customer


# Tìm kiếm nhà hàng theo TÊN NHÀ HÀNG
def get_restaurants_by_name(search_query, page, per_page=12, sort_by='default', user_lat=None, user_lon=None):
    # Fallback cho trường hợp template vẫn gửi 'price'
    if sort_by == 'price':
        sort_by = 'price_low_to_high'
    # Build base query
    query = db.session.query(
        Restaurant,
        func.coalesce(func.avg(Review.rating), 0.0).label('avg_rating')
    ) \
        .outerjoin(Review, Review.restaurant_id == Restaurant.id) \
        .filter(Restaurant.name.ilike(f'%{search_query}%'),
                Restaurant.approval_status == RestaurantApprovalStatus.APPROVED) \
        .group_by(Restaurant.id)

    # Apply sorting
    if sort_by == 'rating':
        query = query.order_by(func.coalesce(func.avg(Review.rating), 0.0).desc())

    elif sort_by == 'price_low_to_high':
        # Get restaurants with their minimum price and sort by it
        subquery = db.session.query(
            MenuItem.restaurant_id,
            func.min(MenuItem.price).label('min_price')
        ).filter(MenuItem.is_active == True).group_by(MenuItem.restaurant_id).subquery()

        query = query.join(subquery, Restaurant.id == subquery.c.restaurant_id) \
            .order_by(subquery.c.min_price.asc())
    elif sort_by == 'price_high_to_low':
        # Get restaurants with their maximum price and sort by it
        subquery = db.session.query(
            MenuItem.restaurant_id,
            func.max(MenuItem.price).label('max_price')
        ).filter(MenuItem.is_active == True).group_by(MenuItem.restaurant_id).subquery()

        query = query.join(subquery, Restaurant.id == subquery.c.restaurant_id) \
            .order_by(subquery.c.max_price.desc())


    elif sort_by == 'distance' and user_lat is not None and user_lon is not None:
        restaurants_with_rating = query.all()
        for restaurant, avg_rating in restaurants_with_rating:
            if restaurant.latitude and restaurant.longitude:
                restaurant.distance = haversine(user_lat, user_lon,
                                                restaurant.latitude, restaurant.longitude)
            else:
                restaurant.distance = None
            restaurant.avg_rating = round(avg_rating, 1) if avg_rating else 0.0

        restaurants_with_rating = sorted(
            restaurants_with_rating,
            key=lambda r: (r[0].distance is None, r[0].distance if r[0].distance is not None else 1e12))
        # paginate thủ công

        start, end = (page - 1) * per_page, page * per_page
        paginated_items = restaurants_with_rating[start:end]
        restaurants = [r[0] for r in paginated_items]
        price_ranges = get_restaurant_price_ranges([r.id for r in restaurants])
        for r in restaurants:
            r.min_price, r.max_price = price_ranges.get(r.id, (0, 0))
        return {
            'restaurants': restaurants,
            'page': page,
            'per_page': per_page,
            'total': len(restaurants_with_rating)
        }
    else:
        query = query.order_by(Restaurant.id)

    # Paginate the query
    restaurants = query.paginate(page=page, per_page=per_page)

    # Get restaurant IDs for price range calculation
    restaurant_ids = [restaurant.id for restaurant, avg_rating in restaurants.items]

    # Get price ranges
    price_ranges = get_restaurant_price_ranges(restaurant_ids)

    results = []
    for restaurant, avg_rating in restaurants.items:
        restaurant.avg_rating = round(avg_rating, 1) if avg_rating else 0.0

        # Add price range
        min_price, max_price = price_ranges.get(restaurant.id, (0, 0))
        restaurant.min_price = min_price
        restaurant.max_price = max_price

        results.append(restaurant)

    return {
        'restaurants': results,
        'page': page,
        'per_page': per_page,
        'total': restaurants.total,
    }

# Tìm món ăn chứa từ khóa, kèm theo thông tin nhà hàng
def get_menu_items_by_name(search_query, page, per_page=12):
    # Sửa lại query để join và lấy kết quả đúng cách
    query = (db.session.query(MenuItem)
             .join(Restaurant, MenuItem.restaurant_id == Restaurant.id)
             .filter(
        MenuItem.name.ilike(f'%{search_query}%'),
        Restaurant.approval_status == RestaurantApprovalStatus.APPROVED,
        MenuItem.is_active == True
    )
             .order_by(MenuItem.id))

    # Phân trang
    paginated_results = query.paginate(page=page, per_page=per_page)

    # Tạo danh sách kết quả
    results = []
    for menu_item in paginated_results.items:
        # Đảm bảo load restaurant information
        menu_item.restaurant = Restaurant.query.get(menu_item.restaurant_id)
        results.append(menu_item)

    return {
        'menu_items': results,
        'page': page,
        'per_page': per_page,
        'total': paginated_results.total
    }

# Tính điểm trung bình cho mỗi nhà hàng
def get_restaurants_by_category(category_id, page, per_page=12, sort_by='default', user_lat=None, user_lon=None):
    # Fallback cho trường hợp template vẫn gửi 'price'
    if sort_by == 'price':
        sort_by = 'price_low_to_high'
    # Build base query
    query = db.session.query(
        Restaurant,
        func.coalesce(func.avg(Review.rating), 0.0).label('avg_rating')
    ) \
        .join(MenuItem, Restaurant.id == MenuItem.restaurant_id) \
        .outerjoin(Review, Review.restaurant_id == Restaurant.id) \
        .filter(MenuItem.category_id == category_id, Restaurant.approval_status == RestaurantApprovalStatus.APPROVED) \
        .group_by(Restaurant.id)

    # Apply sorting
    if sort_by == 'rating':
        query = query.order_by(func.coalesce(func.avg(Review.rating), 0.0).desc())

    elif sort_by == 'price_low_to_high':
        # Get restaurants with their minimum price and sort by it
        subquery = db.session.query(
            MenuItem.restaurant_id,
            func.min(MenuItem.price).label('min_price')
        ).filter(MenuItem.is_active == True).group_by(MenuItem.restaurant_id).subquery()

        query = query.join(subquery, Restaurant.id == subquery.c.restaurant_id) \
            .order_by(subquery.c.min_price.asc())
    elif sort_by == 'price_high_to_low':
        # Get restaurants with their maximum price and sort by it
        subquery = db.session.query(
            MenuItem.restaurant_id,
            func.max(MenuItem.price).label('max_price')
        ).filter(MenuItem.is_active == True).group_by(MenuItem.restaurant_id).subquery()

        query = query.join(subquery, Restaurant.id == subquery.c.restaurant_id) \
            .order_by(subquery.c.max_price.desc())

    elif sort_by == 'distance' and user_lat is not None and user_lon is not None:
        restaurants_with_rating = query.all()
        for restaurant, avg_rating in restaurants_with_rating:
            if restaurant.latitude and restaurant.longitude:
                restaurant.distance = haversine(user_lat, user_lon,
                                                restaurant.latitude, restaurant.longitude)
            else:
                restaurant.distance = None
            restaurant.avg_rating = round(avg_rating, 1) if avg_rating else 0.0

        # Sắp xếp theo distance
        restaurants_with_rating = sorted(
            restaurants_with_rating,
            key=lambda r: (r[0].distance is None, r[0].distance if r[0].distance is not None else 1e12))

        # Phân trang thủ công
        start, end = (page - 1) * per_page, page * per_page
        paginated_items = restaurants_with_rating[start:end]
        restaurants = [r[0] for r in paginated_items]

        # Tính price range
        price_ranges = get_restaurant_price_ranges([r.id for r in restaurants])
        for r in restaurants:
            r.min_price, r.max_price = price_ranges.get(r.id, (0, 0))

        return {
            'restaurants': restaurants,
            'page': page,
            'per_page': per_page,
            'total': len(restaurants_with_rating)
        }
    else:
        query = query.order_by(Restaurant.id)

    # Paginate the query
    restaurants = query.paginate(page=page, per_page=per_page)

    # Get restaurant IDs for price range calculation
    restaurant_ids = [restaurant.id for restaurant, avg_rating in restaurants.items]

    # Get price ranges
    price_ranges = get_restaurant_price_ranges(restaurant_ids)

    # Gán điểm trung bình vào đối tượng nhà hàng
    results = []
    for restaurant, avg_rating in restaurants.items:
        restaurant.avg_rating = round(avg_rating, 1) if avg_rating else 0.0

        # Add price range
        min_price, max_price = price_ranges.get(restaurant.id, (0, 0))
        restaurant.min_price = min_price
        restaurant.max_price = max_price

        results.append(restaurant)

    return {
        'restaurants': results,
        'page': page,
        'per_page': per_page,
        'total': restaurants.total
    }


def get_all_restaurants(page, per_page=12, sort_by='default', user_lat=None, user_lon=None):
    # Build base query
    query = db.session.query(
        Restaurant,
        func.coalesce(func.avg(Review.rating), 0.0).label('avg_rating')
    ) \
        .filter(Restaurant.approval_status == RestaurantApprovalStatus.APPROVED) \
        .outerjoin(Review, Review.restaurant_id == Restaurant.id) \
        .group_by(Restaurant.id)

    # Apply sorting
    if sort_by == 'rating':
        query = query.order_by(func.coalesce(func.avg(Review.rating), 0.0).desc())
    elif sort_by == 'price_low_to_high':
        # Get restaurants with their minimum price and sort by it
        subquery = db.session.query(
            MenuItem.restaurant_id,
            func.min(MenuItem.price).label('min_price')
        ).filter(MenuItem.is_active == True).group_by(MenuItem.restaurant_id).subquery()

        query = query.join(subquery, Restaurant.id == subquery.c.restaurant_id) \
            .order_by(subquery.c.min_price.asc())
    elif sort_by == 'price_high_to_low':
        # Get restaurants with their maximum price and sort by it
        subquery = db.session.query(
            MenuItem.restaurant_id,
            func.max(MenuItem.price).label('max_price')
        ).filter(MenuItem.is_active == True).group_by(MenuItem.restaurant_id).subquery()

        query = query.join(subquery, Restaurant.id == subquery.c.restaurant_id) \
            .order_by(subquery.c.max_price.desc())


    elif sort_by == 'distance' and user_lat is not None and user_lon is not None:
        # Nếu sắp xếp theo khoảng cách và có tọa độ người dùng
        # Lấy tất cả nhà hàng và tính toán khoảng cách trong Python
        restaurants_with_rating = query.all()
        for restaurant, avg_rating in restaurants_with_rating:
            if restaurant.latitude and restaurant.longitude:
                restaurant.distance = haversine(user_lat, user_lon, restaurant.latitude, restaurant.longitude)
            else:
                restaurant.distance = None  # Đặt khoảng cách = none nếu không có tọa độ
        # Sắp xếp danh sách trong Python theo khoảng cách
        restaurants_with_rating = sorted(
            restaurants_with_rating,
            key=lambda r: (r[0].distance is None, r[0].distance if r[0].distance is not None else 1e12))

        # Phân trang thủ công trên danh sách đã sắp xếp
        start = (page - 1) * per_page
        end = start + per_page
        paginated_items = restaurants_with_rating[start:end]
        # Trả về kết quả
        restaurants = [r[0] for r in paginated_items]
        # Bổ sung các thông tin khác
        price_ranges = get_restaurant_price_ranges([r.id for r in restaurants])
        for (res_obj, avg_rating) in [(r[0], r[1]) for r in paginated_items]:
            res_obj.avg_rating = round(avg_rating, 1) if avg_rating else 0.0
            # Gán min/max để template dùng
            min_price, max_price = price_ranges.get(res_obj.id, (0, 0))
            res_obj.min_price = min_price
            res_obj.max_price = max_price
            res_obj.is_open = customer.is_restaurant_open(res_obj)

        return {
            'restaurants': restaurants,
            'page': page,
            'per_page': per_page,
            'total': len(restaurants_with_rating)  # Tổng số nhà hàng
        }
    else:
        query = query.order_by(Restaurant.id)

    # Paginate the query
    restaurants = query.paginate(page=page, per_page=per_page)

    # Get restaurant IDs
    restaurant_ids = [restaurant.id for restaurant, avg_rating in restaurants.items]

    # Get price ranges
    price_ranges = get_restaurant_price_ranges(restaurant_ids)

    # Gán điểm trung bình vào đối tượng nhà hàng
    results = []
    for restaurant, avg_rating in restaurants.items:
        restaurant.avg_rating = round(avg_rating, 1) if avg_rating else 0.0

        # Add price range
        min_price, max_price = price_ranges.get(restaurant.id, (0, 0))
        restaurant.min_price = min_price
        restaurant.max_price = max_price

        results.append(restaurant)

    return {
        'restaurants': results,
        'page': page,
        'per_page': per_page,
        'total': restaurants.total
    }

def get_menu_item_by_id(menu_item_id):
    """
    Lấy thông tin món ăn theo ID
    """
    return MenuItem.query.get(menu_item_id)


def get_orders_history(customer_id):
    orders = Order.query.filter_by(customer_id=customer_id) \
        .filter(Order.status.in_([OrderStatus.COMPLETED, OrderStatus.CANCELLED])) \
        .options(
        db.joinedload(Order.restaurant),
        db.joinedload(Order.order_items).joinedload(OrderItem.menu_item)
    ) \
        .order_by(Order.created_at.desc()) \
        .all()

    return orders

def apply_promo(promo_code, total_price):
    """Áp dụng mã giảm giá"""
    promo = PromoCode.query.filter_by(code=promo_code).first()
    if not promo:
        return {'success': False, 'message': 'Mã giảm giá không tồn tại'}

    current_time = datetime.now()
    if current_time < promo.start_date or current_time > promo.end_date:
        return {'success': False, 'message': 'Mã giảm giá đã hết hạn'}

    discount_value = float(promo.discount_value)
    if promo.discount_type == DiscountType.PERCENT:
        discount_amount = total_price * (discount_value / 100)
    else:  # FIXED
        discount_amount = discount_value

    # Đảm bảo không giảm quá tổng tiền
    discount_amount = min(discount_amount, total_price)
    final_amount = total_price - discount_amount

    return {
        'success': True,
        'discount_amount': discount_amount,
        'final_amount': final_amount
    }

def place_order(customer_id, order_data, checkout_data):
    """Đặt hàng"""
    if not checkout_data:
        return {'success': False, 'message': 'Không có dữ liệu thanh toán'}

    grouped_items = checkout_data['grouped_items']
    total_amount = checkout_data['total_price']

    # Lấy restaurant_id từ món đầu tiên
    first_restaurant = next(iter(grouped_items.keys()))
    first_item = grouped_items[first_restaurant][0]
    menu_item = MenuItem.query.get(first_item['id'])
    restaurant_id = menu_item.restaurant_id

    # Xử lý mã giảm giá nếu có
    promo_id = None
    if order_data.get('applied_promo'):
        promo = PromoCode.query.filter_by(code=order_data['applied_promo']['code']).first()
        if promo:
            promo_id = promo.id
            total_amount = order_data['applied_promo']['final_amount']

    # Tạo đơn hàng
    new_order = Order(
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        promo_code_id=promo_id,
        total_amount=total_amount,
        status=OrderStatus.PENDING
    )
    db.session.add(new_order)
    db.session.flush()

    # Thêm các món vào đơn hàng
    for restaurant, items in grouped_items.items():
        for item in items:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item['id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)

    # Tạo thanh toán
    payment = Payment(
        order_id=new_order.id,
        amount=total_amount,
        method=PaymentMethod(order_data['payment_method']),
        status=PaymentStatus.PENDING
    )
    db.session.add(payment)
    db.session.commit()

    return {
        'success': True,
        'order_id': new_order.id
    }


# Add this function to calculate price ranges
def get_restaurant_price_ranges(restaurant_ids):
    """
    Calculate min and max prices for given restaurant IDs
    """
    price_ranges = db.session.query(
        MenuItem.restaurant_id,
        func.min(MenuItem.price).label('min_price'),
        func.max(MenuItem.price).label('max_price')
    ).filter(
        MenuItem.restaurant_id.in_(restaurant_ids),
        MenuItem.is_active == True
    ).group_by(MenuItem.restaurant_id).all()

    return {r.restaurant_id: (r.min_price, r.max_price) for r in price_ranges}

def get_vietnam_time():
    # Get current time in Vietnam timezone (UTC+7)
    utc_now = datetime.utcnow()
    vietnam_offset = timedelta(hours=7)
    vietnam_time = utc_now + vietnam_offset
    return vietnam_time.time()

def _is_open_now(opening, closing, now):
    if not opening or not closing:
        return False
    if opening <= closing:
        return opening <= now < closing
    else:
        return now >= opening or now < closing


def haversine(lat1, lon1, lat2, lon2):
    # Chuyển độ sang radian
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Tính khoảng cách
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Bán kính Trái Đất (km)
    return c * r


# customer_service.py
# def send_sms(to_phone, message):
#     try:
#         # Sửa định dạng số điện thoại
#         if to_phone.startswith('0'):
#             to_phone = '+84' + to_phone[1:]  # Chuẩn quốc tế: +84xxxxxxxxx
#
#         api_key = current_app.config['VONAGE_API_KEY']
#         api_secret = current_app.config['VONAGE_API_SECRET']
#         brand_name = current_app.config['VONAGE_BRAND_NAME']
#
#         url = "https://rest.nexmo.com/sms/json"
#
#         # Sửa lỗi Unicode - GỬI DẠNG UNICODE
#         payload = {
#             "from": brand_name,
#             "text": message,
#             "to": to_phone,
#             "api_key": api_key,
#             "api_secret": api_secret,
#             "type": "unicode"  # QUAN TRỌNG: Dùng cho ký tự đặc biệt
#         }
#
#         response = requests.post(url, data=payload)
#         result = response.json()
#
#         # Debug: Log toàn bộ response
#         current_app.logger.info(f"Vonage full response: {json.dumps(result, indent=2)}")
#
#         if result['messages'][0]['status'] == '0':
#             return True
#         else:
#             error_text = result['messages'][0]['error-text']
#             current_app.logger.error(f"Failed to send SMS: {error_text}")
#             return False
#     except Exception as e:
#         current_app.logger.error(f"SMS error: {str(e)}")
#         return False