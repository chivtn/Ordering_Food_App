from OrderingFoodApp import init_app, db
from OrderingFoodApp.models import *
from faker import Faker
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta  # Thêm import ở đầu file nếu chưa có

fake = Faker('vi_VN')

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
    for i in range(1, 6):  # 5 chủ nhà hàng
        owner = User(
            name=fake.name(),
            email=f"owner{i}@example.com",
            password=generate_password_hash("owner123"),
            role=UserRole.OWNER
        )
        db.session.add(owner)
        db.session.flush()
        owners.append(owner)

    # ========== TẠO KHÁCH HÀNG ==========
    customers = []
    for i in range(1, 6):  # 5 khách hàng
        customer = User(
            name=fake.name(),
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
    {"name": "Khai Vị", "image_url": "https://img.lovepik.com/png/20231111/appetizer-clipart-platter-of-food-is-arranged-on-top-cartoon_558150_wh1200.png"},
    {"name": "Món Chính", "image_url": "https://png.pngtree.com/png-vector/20240528/ourlarge/pngtree-a-chinese-style-cuisine-looking-beautiful-png-image_12504550.png"},
    {"name": "Tráng Miệng", "image_url": "https://img.lovepik.com/png/20231107/Piece-of-cake-cartoon-pastry-illustration-strawberry-snack_520860_wh860.png"},
    {"name": "Đồ Uống", "image_url": "https://img.lovepik.com/free-png/20210927/lovepik-drink-png-image_401579146_wh1200.png"}
]
    categories = []
    for data in category_names:
        cat = MenuCategory(name=data["name"], image_url=data["image_url"])
        db.session.add(cat)
        db.session.flush()
        categories.append(cat)

    # ========== TÊN NHÀ HÀNG & MÓN ĂN ĐA DẠNG ==========
    restaurant_types = [
        ("Fast Food Hub", ["Burger", "Pizza", "Fried Chicken", "French Fries"]),
        ("Healthy Corner", ["Salad", "Smoothie Bowl", "Vegan Wrap", "Detox Juice"]),
        ("Cafe Chill", ["Latte", "Cappuccino", "Matcha", "Cheesecake"]),
        ("BBQ & Hotpot", ["Lẩu Thái", "Lẩu Bò", "Nướng BBQ", "Hải sản nướng"]),
        ("Asian Delights", ["Sushi", "Ramen", "Pad Thai", "Bánh Mì"])
    ]

    restaurants = []
    menu_items = []

    for owner in owners:
        for _ in range(random.randint(2, 6)):  # Mỗi chủ 2-3 nhà hàng
            rest_type = random.choice(restaurant_types)
            restaurant = Restaurant(
                owner_id=owner.id,
                name=f"{rest_type[0]} {fake.city_suffix()}",
                description=fake.text(max_nb_chars=150),
                address=fake.address(),
                phone=fake.phone_number(),
                latitude=random.uniform(10.75, 10.80),
                longitude=random.uniform(106.65, 106.70),
                image_url=f"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNRas_-SFKO__MFuzdDpDJX1N-lQ4uhw2ODw&s"  # Thêm dòng này
            )
            db.session.add(restaurant)
            db.session.flush()
            restaurants.append(restaurant)

            # Tạo món ăn
            for cat in categories:
                for _ in range(random.randint(3, 5)):  # 3–5 món mỗi danh mục
                    dish_name = random.choice(rest_type[1])
                    menu_item = MenuItem(
                        restaurant_id=restaurant.id,
                        category_id=cat.id,
                        name=f"{dish_name} {fake.word().capitalize()}",
                        description=f"Món {dish_name} yêu thích của giới trẻ và dân văn phòng.",
                        price=random.randint(30000, 120000),
                        image_url="https://food-cms.grab.com/compressed_webp/items/VNITE2025021904274992700/detail/menueditor_item_b63ce334b95042ed85f8e266b6724540_1739939243566377306.webp"
                    )
                    db.session.add(menu_item)
                    menu_items.append(menu_item)

    db.session.commit()

    # ========== TẠO GIỎ HÀNG & ĐƠN HÀNG ==========
    for customer in customers:
        for _ in range(5):  # 👉 Mỗi khách hàng tạo 5 đơn hàng
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
            payment = Payment(
                order_id=order.id,
                amount=total_amount,
                method=PaymentMethod.CASH_ON_DELIVERY,
                status=PaymentStatus.COMPLETED
            )
            db.session.add(payment)

            # Đánh giá
            review = Review(
                customer_id=customer.id,
                restaurant_id=selected_restaurant.id,
                order_id=order.id,
                rating=random.randint(4, 5),
                comment=fake.sentence(nb_words=12)
            )
            db.session.add(review)
            db.session.flush()

            # Phản hồi đánh giá
            response = ReviewResponse(
                review_id=review.id,
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

# ─── BỔ SUNG PROFILE & ADDRESS CHO TẤT CẢ USER ───
    # gom tất cả users vừa tạo
    all_users = [admin] + owners + customers

    # ========== TẠO 10 MÃ KHUYẾN MÃI GIẢ ==========
    promo_image_urls = [
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

    for i in range(10):
        code = f"SALE{random.randint(100, 999)}"
        promo = PromoCode(
            code=code,
            description=fake.sentence(nb_words=8),
            discount_type=random.choice([DiscountType.PERCENT, DiscountType.FIXED]),
            discount_value=random.randint(5, 50) if i % 2 == 0 else random.randint(10000, 100000),
            start_date=datetime(2025, 7, random.randint(1, 10)),
end_date=datetime(2025, 8, random.randint(20, 31)),
            usage_limit=random.choice([10, 20, 50, 100]),
            image_url=promo_image_urls[i % len(promo_image_urls)]
        )
        db.session.add(promo)

    db.session.commit()

    for user in all_users:
        # 1) Gán ngày sinh, giới tính, số điện thoại
        user.date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=60)
        user.gender        = random.choice(list(Gender))
        user.phone         = fake.phone_number()
        db.session.add(user)

        # 2) Tạo địa chỉ mặc định
        addr_def = Address(
            user_id      = user.id,
            address_line = fake.address(),
            is_default   = True
        )
        db.session.add(addr_def)

        # 3) Tạo thêm 1–3 địa chỉ phụ
        for _ in range(random.randint(1, 3)):
            addr = Address(
                user_id      = user.id,
                address_line = fake.address(),
                is_default   = False
            )
            db.session.add(addr)

    db.session.commit()

    print("✅ Seed thành công")

if __name__ == '__main__':
    app = init_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data()