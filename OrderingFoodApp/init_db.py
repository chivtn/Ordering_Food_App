# from OrderingFoodApp import init_app, db
# from OrderingFoodApp.models import *
# from faker import Faker
# from werkzeug.security import generate_password_hash
# import random
# from datetime import datetime, timedelta
#
# fake = Faker('vi_VN')
#
#
# def seed_data():
#     # ========== ADMIN ==========
#     admin = User(
#         name="Quản trị viên",
#         email="admin@example.com",
#         password=generate_password_hash("admin123"),
#         role=UserRole.ADMIN
#     )
#     db.session.add(admin)
#
#     # ========== TẠO CHỦ NHÀ HÀNG ==========
#     owners = []
#     for i in range(1, 6):  # 5 chủ nhà hàng
#         owner = User(
#             name=fake.name(),
#             email=f"owner{i}@example.com",
#             password=generate_password_hash("owner123"),
#             role=UserRole.OWNER
#         )
#         db.session.add(owner)
#         db.session.flush()
#         owners.append(owner)
#
#     # ========== TẠO KHÁCH HÀNG ==========
#     customers = []
#     for i in range(1, 6):  # 5 khách hàng
#         customer = User(
#             name=fake.name(),
#             email=f"customer{i}@example.com",
#             password=generate_password_hash("customer123"),
#             role=UserRole.CUSTOMER
#         )
#         db.session.add(customer)
#         db.session.flush()
#         customers.append(customer)
#
#     db.session.commit()
#
#     # ========== DANH MỤC MÓN ĂN ==========
#     category_names = [
#         {"name": "Khai Vị",
#          "image_url": "https://img.lovepik.com/png/20231111/appetizer-clipart-platter-of-food-is-arranged-on-top-cartoon_558150_wh1200.png"},
#         {"name": "Món Chính",
#          "image_url": "https://png.pngtree.com/png-vector/20240528/ourlarge/pngtree-a-chinese-style-cuisine-looking-beautiful-png-image_12504550.png"},
#         {"name": "Tráng Miệng",
#          "image_url": "https://img.lovepik.com/png/20231107/Piece-of-cake-cartoon-pastry-illustration-strawberry-snack_520860_wh860.png"},
#         {"name": "Đồ Uống",
#          "image_url": "https://img.lovepik.com/free-png/20210927/lovepik-drink-png-image_401579146_wh1200.png"}
#     ]
#     categories = []
#     for data in category_names:
#         cat = MenuCategory(name=data["name"], image_url=data["image_url"])
#         db.session.add(cat)
#         db.session.flush()
#         categories.append(cat)
#
#     # ========== TÊN NHÀ HÀNG & MÓN ĂN ĐA DẠNG ==========
#     restaurant_types = [
#         ("Fast Food Hub", ["Burger", "Pizza", "Fried Chicken", "French Fries"]),
#         ("Healthy Corner", ["Salad", "Smoothie Bowl", "Vegan Wrap", "Detox Juice"]),
#         ("Cafe Chill", ["Latte", "Cappuccino", "Matcha", "Cheesecake"]),
#         ("BBQ & Hotpot", ["Lẩu Thái", "Lẩu Bò", "Nướng BBQ", "Hải sản nướng"]),
#         ("Asian Delights", ["Sushi", "Ramen", "Pad Thai", "Bánh Mì"])
#     ]
#
#     restaurants = []
#     menu_items = []
#
#     for owner in owners:
#         for _ in range(random.randint(2, 6)):  # Mỗi chủ 2-3 nhà hàng
#             rest_type = random.choice(restaurant_types)
#             restaurant = Restaurant(
#                 owner_id=owner.id,
#                 name=f"{rest_type[0]} {fake.city_suffix()}",
#                 description=fake.text(max_nb_chars=150),
#                 address=fake.address(),
#                 phone=fake.phone_number(),
#                 latitude=random.uniform(10.75, 10.80),
#                 longitude=random.uniform(106.65, 106.70),
#                 image_url=f"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNRas_-SFKO__MFuzdDpDJX1N-lQ4uhw2ODw&s"
#                 # Thêm dòng này
#             )
#             db.session.add(restaurant)
#             db.session.flush()
#             restaurants.append(restaurant)
#
#             # Tạo món ăn
#             for cat in categories:
#                 for _ in range(random.randint(3, 5)):  # 3–5 món mỗi danh mục
#                     dish_name = random.choice(rest_type[1])
#                     menu_item = MenuItem(
#                         restaurant_id=restaurant.id,
#                         category_id=cat.id,
#                         name=f"{dish_name} {fake.word().capitalize()}",
#                         description=f"Món {dish_name} yêu thích của giới trẻ và dân văn phòng.",
#                         price=random.randint(30000, 120000),
#                         image_url="https://food-cms.grab.com/compressed_webp/items/VNITE2025021904274992700/detail/menueditor_item_b63ce334b95042ed85f8e266b6724540_1739939243566377306.webp"
#                     )
#                     db.session.add(menu_item)
#                     menu_items.append(menu_item)
#
#     db.session.commit()
#
#     # ========== TẠO GIỎ HÀNG & ĐƠN HÀNG ==========
#     for customer in customers:
#         for _ in range(5):  # 👉 Mỗi khách hàng tạo 5 đơn hàng
#             selected_restaurant = random.choice(restaurants)
#             items = MenuItem.query.filter_by(restaurant_id=selected_restaurant.id).limit(4).all()
#
#             # Giỏ hàng
#             cart = Cart(customer_id=customer.id)
#             db.session.add(cart)
#             db.session.flush()
#             for item in items:
#                 cart_item = CartItem(
#                     cart_id=cart.id,
#                     menu_item_id=item.id,
#                     quantity=random.randint(1, 3)
#                 )
#                 db.session.add(cart_item)
#
#             # Đơn hàng
#             total_amount = sum(item.price * 2 for item in items)
#
#             # Random trạng thái đơn hàng
#             order_status = random.choice([
#                 OrderStatus.PENDING,
#                 OrderStatus.CONFIRMED,
#                 OrderStatus.PREPARING,
#                 OrderStatus.COMPLETED,
#                 OrderStatus.CANCELLED
#             ])
#
#             order = Order(
#                 customer_id=customer.id,
#                 restaurant_id=selected_restaurant.id,
#                 total_amount=total_amount,
#                 status=order_status
#             )
#
#             db.session.add(order)
#             db.session.flush()
#
#             for item in items:
#                 order_item = OrderItem(
#                     order_id=order.id,
#                     menu_item_id=item.id,
#                     quantity=2,
#                     price=item.price
#                 )
#                 db.session.add(order_item)
#
#             # Thanh toán
#             payment_status = PaymentStatus.COMPLETED if order_status == OrderStatus.COMPLETED else PaymentStatus.PENDING
#             payment = Payment(
#                 order_id=order.id,
#                 amount=total_amount,
#                 method=PaymentMethod.CASH_ON_DELIVERY,
#                 status=payment_status
#             )
#             db.session.add(payment)
#
#             # Đánh giá
#             review = None
#             if order_status == OrderStatus.COMPLETED:
#                 review = Review(
#                     customer_id=customer.id,
#                     restaurant_id=selected_restaurant.id,
#                     order_id=order.id,
#                     rating=random.randint(4, 5),
#                     comment=fake.sentence(nb_words=12)
#                 )
#                 db.session.add(review)
#
#                 # Phản hồi đánh giá
#                 response = ReviewResponse(
#                     review=review,  # dùng relationship thay vì review_id
#                     owner_id=selected_restaurant.owner_id,
#                     response_text="Cảm ơn bạn đã ủng hộ quán!"
#                 )
#                 db.session.add(response)
#
#
#             # Thông báo
#             notification = Notification(
#                 user_id=customer.id,
#                 type=NotificationType.ORDER_STATUS,
#                 message=f"Đơn hàng #{order.id} đã được xác nhận.",
#                 is_read=False
#             )
#             db.session.add(notification)
#
#     db.session.commit()
#
#     # ─── BỔ SUNG PROFILE & ADDRESS CHO TẤT CẢ USER ───
#     # gom tất cả users vừa tạo
#     all_users = [admin] + owners + customers
#
#     # ========== TẠO 10 MÃ KHUYẾN MÃI GIẢ ==========
#     promo_image_urls = [
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
#         "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg"
#     ]
#
#     for i in range(10):
#         code = f"SALE{random.randint(100, 999)}"
#         promo = PromoCode(
#             code=code,
#             description=fake.sentence(nb_words=8),
#             discount_type=random.choice([DiscountType.PERCENT, DiscountType.FIXED]),
#             discount_value=random.randint(5, 50) if i % 2 == 0 else random.randint(10000, 100000),
#             start_date=datetime(2025, 7, random.randint(1, 10)),
#             end_date=datetime(2025, 8, random.randint(20, 31)),
#             usage_limit=random.choice([10, 20, 50, 100]),
#             image_url=promo_image_urls[i % len(promo_image_urls)]
#         )
#         db.session.add(promo)
#
#     db.session.commit()
#
#     for user in all_users:
#         # 1) Gán ngày sinh, giới tính, số điện thoại
#         user.date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=60)
#         user.gender = random.choice(list(Gender))
#         user.phone = fake.phone_number()
#         db.session.add(user)
#
#         # 2) Tạo địa chỉ mặc định
#         addr_def = Address(
#             user_id=user.id,
#             address_line=fake.address(),
#             is_default=True
#         )
#         db.session.add(addr_def)
#
#         # 3) Tạo thêm 1–3 địa chỉ phụ
#         for _ in range(random.randint(1, 3)):
#             addr = Address(
#                 user_id=user.id,
#                 address_line=fake.address(),
#                 is_default=False
#             )
#             db.session.add(addr)
#
#     db.session.commit()
#
#     print("✅ Seed thành công")
#
#
# if __name__ == '__main__':
#     app = init_app()
#     with app.app_context():
#         db.drop_all()
#         db.create_all()
#         seed_data()
#

from OrderingFoodApp import init_app, db
from OrderingFoodApp.models import *
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, time


def seed_data():
    # ========== ADMIN ==========
    admin = User(
        name="Quản trị viên",
        email="admin@example.com",
        password=generate_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    db.session.add(admin)

    # ========== TẠO CHỦ NHÀ HÀNG ==========
    owners = []
    owner_names = ["Nguyễn Văn A", "Trần Thị B", "Lê Văn C"]
    for i in range(1, 4):  # 3 chủ nhà hàng
        owner = User(
            name=owner_names[i - 1],
            email=f"owner{i}@example.com",
            password=generate_password_hash("owner123"),
            role=UserRole.OWNER
        )
        db.session.add(owner)
        db.session.flush()
        owners.append(owner)

    # ========== TẠO KHÁCH HÀNG ==========
    customers = []
    customer_names = ["Quang Mai", "Đỗ Thị Giàu", "Hà Đức Dương", "Bùi Thị Khanh", "Đặng Văn Linh"]
    for i in range(1, 6):  # 5 khách hàng
        customer = User(
            name=customer_names[i - 1],
            email=f"customer{i}@example.com",
            password=generate_password_hash("customer123"),
            role=UserRole.CUSTOMER
        )
        db.session.add(customer)
        db.session.flush()
        customers.append(customer)

    db.session.commit()

    # ========== DANH MỤC MÓN ĂN ==========
    category_names = [
        {"name": "Khai Vị",
         "image_url": "https://img.lovepik.com/png/20231111/appetizer-clipart-platter-of-food-is-arranged-on-top-cartoon_558150_wh1200.png"},
        {"name": "Món Chính",
         "image_url": "https://png.pngtree.com/png-vector/20240528/ourlarge/pngtree-a-chinese-style-cuisine-looking-beautiful-png-image_12504550.png"},
        {"name": "Tráng Miệng",
         "image_url": "https://img.lovepik.com/png/20231107/Piece-of-cake-cartoon-pastry-illustration-strawberry-snack_520860_wh860.png"},
        {"name": "Đồ Uống",
         "image_url": "https://img.lovepik.com/free-png/20210927/lovepik-drink-png-image_401579146_wh1200.png"}
    ]
    categories = []
    for data in category_names:
        cat = MenuCategory(name=data["name"], image_url=data["image_url"])
        db.session.add(cat)
        db.session.flush()
        categories.append(cat)

    # ========== NHÀ HÀNG & MÓN ĂN THỰC TẾ TẠI TP.HCM ==========
    restaurants_data = [
        {
            "name": "Phở Hòa Pasteur",
            "description": "Quán phở nổi tiếng tại Sài Gòn với hương vị truyền thống",
            "address": "260C Pasteur, Phường 8, Quận 3, TP.HCM",
            "phone": "028 3829 7943",
            "latitude": 10.7829,
            "longitude": 106.6922,
            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNRas_-SFKO__MFuzdDpDJX1N-lQ4uhw2ODw&s",
            "menu_items": {
                "Khai Vị": ["Gỏi cuốn", "Chả giò", "Bò lá lốt"],
                "Món Chính": ["Phở bò", "Phở gà", "Bún bò Huế"],
                "Tráng Miệng": ["Chè đậu xanh", "Rau câu"],
                "Đồ Uống": ["Trà đá", "Nước cam", "Sinh tố"]
            }
        },
        {
            "name": "Bánh Mì Huỳnh Hoa",
            "description": "Tiệm bánh mì ngon nhất Sài Gòn",
            "address": "26 Lê Thị Riêng, Phường Bến Thành, Quận 1, TP.HCM",
            "phone": "090 909 0909",
            "latitude": 10.7715,
            "longitude": 106.6984,
            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNRas_-SFKO__MFuzdDpDJX1N-lQ4uhw2ODw&s",
            "menu_items": {
                "Khai Vị": ["Bánh mì chảo"],
                "Món Chính": ["Bánh mì thịt", "Bánh mì xíu mại", "Bánh mì pate"],
                "Tráng Miệng": ["Bánh flan"],
                "Đồ Uống": ["Sữa đậu nành", "Cà phê sữa"]
            }
        },
        {
            "name": "Cơm Tấm Cali",
            "description": "Cơm tấm ngon với nhiều lựa chọn",
            "address": "456 Nguyễn Đình Chiểu, Phường 4, Quận 3, TP.HCM",
            "phone": "028 3832 4567",
            "latitude": 10.7745,
            "longitude": 106.6879,
            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNRas_-SFKO__MFuzdDpDJX1N-lQ4uhw2ODw&s",
            "menu_items": {
                "Khai Vị": ["Gỏi đu đủ khô bò"],
                "Món Chính": ["Cơm tấm sườn", "Cơm tấm bì", "Cơm tấm chả"],
                "Tráng Miệng": ["Chuối chiên"],
                "Đồ Uống": ["Nước mía", "Trà đá"]
            }
        },
        {
            "name": "Quán Ụt Ụt",
            "description": "Chuyên các món nướng BBQ",
            "address": "168 Lê Thánh Tôn, Phường Bến Thành, Quận 1, TP.HCM",
            "phone": "028 3823 4567",
            "latitude": 10.7723,
            "longitude": 106.7012,
            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNRas_-SFKO__MFuzdDpDJX1N-lQ4uhw2ODw&s",
            "menu_items": {
                "Khai Vị": ["Gỏi bò", "Gỏi ngó sen"],
                "Món Chính": ["Bò nướng", "Heo nướng", "Hải sản nướng"],
                "Tráng Miệng": ["Kem", "Chè khúc bạch"],
                "Đồ Uống": ["Bia", "Nước ngọt"]
            }
        },
        {
            "name": "Pizza 4P's",
            "description": "Pizza Ý chất lượng cao",
            "address": "8/15 Lê Thánh Tôn, Phường Bến Nghé, Quận 1, TP.HCM",
            "phone": "028 3822 0500",
            "latitude": 10.7756,
            "longitude": 106.7034,
            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNRas_-SFKO__MFuzdDpDJX1N-lQ4uhw2ODw&s",
            "menu_items": {
                "Khai Vị": ["Salad Ý", "Bruschetta"],
                "Món Chính": ["Pizza Margherita", "Pizza hải sản", "Mỳ Ý"],
                "Tráng Miệng": ["Tiramisu", "Gelato"],
                "Đồ Uống": ["Rượu vang", "Cocktail"]
            }
        }
    ]

    restaurants = []
    menu_items = []

    # Phân bổ nhà hàng cho các chủ (2, 2, 1)
    owner_restaurant_counts = [2, 2, 1]
    assigned_restaurants = set()  # Theo dõi nhà hàng đã được gán

    for i, owner in enumerate(owners):
        count = owner_restaurant_counts[i] if i < len(owner_restaurant_counts) else 0
        available_restaurants = [r for r in restaurants_data if r["name"] not in assigned_restaurants]

        # Chọn ngẫu nhiên số lượng nhà hàng cần gán
        selected_restaurants = random.sample(available_restaurants, min(count, len(available_restaurants)))

        for rest_data in selected_restaurants:
            restaurant = Restaurant(
                owner_id=owner.id,
                name=rest_data["name"],
                description=rest_data["description"],
                address=rest_data["address"],
                phone=rest_data["phone"],
                latitude=rest_data["latitude"],
                longitude=rest_data["longitude"],
                image_url=rest_data["image_url"],
                opening_time=time(7, 0),
                closing_time=time(22, 0)
            )
            db.session.add(restaurant)
            db.session.flush()
            restaurants.append(restaurant)
            assigned_restaurants.add(rest_data["name"])  # Đánh dấu đã gán

            # Tạo món ăn theo danh mục
            for cat in categories:
                if cat.name in rest_data["menu_items"]:
                    for dish_name in rest_data["menu_items"][cat.name]:
                        menu_item = MenuItem(
                            restaurant_id=restaurant.id,
                            category_id=cat.id,
                            name=dish_name,
                            description=f"Món {dish_name} đặc trưng của {restaurant.name}",
                            price=random.randint(30000, 120000),
                            image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNRas_-SFKO__MFuzdDpDJX1N-lQ4uhw2ODw&s",
                            is_active=True
                        )
                        db.session.add(menu_item)
                        menu_items.append(menu_item)

    db.session.commit()
    # ========== TẠO GIỎ HÀNG & ĐƠN HÀNG ==========
    for customer in customers:
        for _ in range(5):  # Mỗi khách hàng tạo 5 đơn hàng
            selected_restaurant = random.choice(restaurants)
            items = MenuItem.query.filter_by(restaurant_id=selected_restaurant.id).limit(4).all()

            # Giỏ hàng
            cart = Cart(customer_id=customer.id)
            db.session.add(cart)
            db.session.flush()
            for item in items:
                cart_item = CartItem(
                    cart_id=cart.id,
                    menu_item_id=item.id,
                    quantity=random.randint(1, 3)
                )
                db.session.add(cart_item)

            # Đơn hàng
            total_amount = sum(item.price * 2 for item in items)

            # Random trạng thái đơn hàng
            order_status = random.choice([
                OrderStatus.PENDING,
                OrderStatus.CONFIRMED,
                OrderStatus.PREPARING,
                OrderStatus.COMPLETED,
                OrderStatus.CANCELLED
            ])

            order = Order(
                customer_id=customer.id,
                restaurant_id=selected_restaurant.id,
                total_amount=total_amount,
                status=order_status
            )

            db.session.add(order)
            db.session.flush()

            for item in items:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item.id,
                    quantity=2,
                    price=item.price
                )
                db.session.add(order_item)

            # Thanh toán
            payment_status = PaymentStatus.COMPLETED if order_status == OrderStatus.COMPLETED else PaymentStatus.PENDING
            payment = Payment(
                order_id=order.id,
                amount=total_amount,
                method=PaymentMethod.CASH_ON_DELIVERY,
                status=payment_status
            )
            db.session.add(payment)

            # Đánh giá
            review = None
            if order_status == OrderStatus.COMPLETED:
                review = Review(
                    customer_id=customer.id,
                    restaurant_id=selected_restaurant.id,
                    order_id=order.id,
                    rating=random.randint(4, 5),
                    comment=f"Rất hài lòng với dịch vụ và chất lượng món ăn tại {selected_restaurant.name}"
                )
                db.session.add(review)

                # Phản hồi đánh giá
                response = ReviewResponse(
                    review=review,
                    owner_id=selected_restaurant.owner_id,
                    response_text="Cảm ơn bạn đã ủng hộ quán!"
                )
                db.session.add(response)

            # Thông báo
            notification = Notification(
                user_id=customer.id,
                type=NotificationType.ORDER_STATUS,
                message=f"Đơn hàng #{order.id} đã được xác nhận.",
                is_read=False
            )
            db.session.add(notification)

    db.session.commit()

    # ========== TẠO PROFILE & ADDRESS CHO USER ==========
    all_users = [admin] + owners + customers
    addresses_tphcm = [
        "123 Nguyễn Huệ, Quận 1",
        "456 Lê Lợi, Quận 1",
        "789 Cách Mạng Tháng 8, Quận 3",
        "321 Võ Văn Tần, Quận 3",
        "654 Nguyễn Thị Minh Khai, Quận 3",
        "987 Lê Văn Sỹ, Phú Nhuận",
        "159 Phan Xích Long, Phú Nhuận",
        "753 Điện Biên Phủ, Bình Thạnh",
        "951 Xô Viết Nghệ Tĩnh, Bình Thạnh",
        "357 Lê Quang Định, Gò Vấp"
    ]

    for user in all_users:
        # Thông tin profile
        user.date_of_birth = datetime(1990 + random.randint(0, 20), random.randint(1, 12), random.randint(1, 28))
        user.gender = random.choice(list(Gender))
        user.phone = f"09{random.randint(10000000, 99999999)}"
        db.session.add(user)

        # Địa chỉ mặc định
        addr_def = Address(
            user_id=user.id,
            address_line=random.choice(addresses_tphcm),
            is_default=True
        )
        db.session.add(addr_def)

        # Thêm 1-3 địa chỉ phụ
        for _ in range(random.randint(1, 3)):
            addr = Address(
                user_id=user.id,
                address_line=random.choice(addresses_tphcm),
                is_default=False
            )
            db.session.add(addr)

    # ========== TẠO MÃ KHUYẾN MÃI ==========
    promo_image_url = [
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg",
        "https://olymstore.net/storage/15.11.2023/Olymstore%20001519%20(1).jpg"
    ]
    promo_codes = [
        {
            "code": "SALE20",
            "description": "Giảm 20% cho đơn hàng từ 200k",
            "discount_type": DiscountType.PERCENT,
            "discount_value": 20,
            "start_date": datetime(2025, 7, 1),
            "end_date": datetime(2025, 8, 31),
            "usage_limit": 100
        },
        {
            "code": "FREESHIP",
            "description": "Miễn phí vận chuyển",
            "discount_type": DiscountType.FIXED,
            "discount_value": 20000,
            "start_date": datetime(2025, 7, 15),
            "end_date": datetime(2025, 8, 15),
            "usage_limit": 50
        },
        {
            "code": "HOTDEAL",
            "description": "Giảm 50k cho đơn hàng từ 150k",
            "discount_type": DiscountType.FIXED,
            "discount_value": 50000,
            "start_date": datetime(2025, 8, 1),
            "end_date": datetime(2025, 8, 31),
            "usage_limit": 200
        }
    ]

    for promo in promo_codes:
        pc = PromoCode(
            code=promo["code"],
            description=promo["description"],
            discount_type=promo["discount_type"],
            discount_value=promo["discount_value"],
            start_date=promo["start_date"],
            end_date=promo["end_date"],
            usage_limit=promo["usage_limit"],
            image_url=promo_image_url[i % len(promo_image_url)]
        )
        db.session.add(pc)

    db.session.commit()

    print("✅ Seed thành công")


if __name__ == '__main__':
    app = init_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data()
