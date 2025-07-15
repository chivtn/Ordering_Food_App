from OrderingFoodApp import db
from OrderingFoodApp.models import User, UserRole  # Import User và UserRole từ models.py
from sqlalchemy.exc import SQLAlchemyError  # Để xử lý lỗi database


def get_all_users(page=1, page_size=10, query=None, role=None):
    """
    Lấy tất cả người dùng với phân trang, tìm kiếm và lọc theo vai trò.
    :param page: Trang hiện tại.
    :param page_size: Số lượng người dùng trên mỗi trang.
    :param query: Chuỗi tìm kiếm (theo tên hoặc email).
    :param role: Lọc theo vai trò (UserRole.ADMIN, UserRole.OWNER, UserRole.CUSTOMER).
    :return: Đối tượng Pagination của Flask-SQLAlchemy.
    """
    try:
        users_query = User.query

        if query:
            # Tìm kiếm theo tên hoặc email (không phân biệt hoa thường)
            search_pattern = f"%{query.lower()}%"
            users_query = users_query.filter(
                (User.name.ilike(search_pattern)) |
                (User.email.ilike(search_pattern))
            )

        if role:
            # Lọc theo vai trò
            if isinstance(role, str):  # Nếu role được truyền dưới dạng chuỗi
                role = UserRole[role.upper()]  # Chuyển đổi chuỗi thành Enum
            users_query = users_query.filter_by(role=role)

        # # Sắp xếp theo ID giảm dần (người dùng mới nhất lên đầu)
        # users_query = users_query.order_by(User.id.desc())

        # Sắp xếp theo ID giảm dần (người dùng mới nhất lên đầu)
        users_query = users_query.order_by(User.id.asc())

        # Thực hiện phân trang
        pagination = users_query.paginate(page=page, per_page=page_size, error_out=False)
        return pagination
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback nếu có lỗi database
        print(f"Error fetching all users: {e}")
        return None  # Hoặc raise e, tùy vào cách bạn muốn xử lý lỗi


def get_user_by_id(user_id):
    """
    Lấy một người dùng theo ID.
    :param user_id: ID của người dùng.
    :return: Đối tượng User hoặc None nếu không tìm thấy.
    """
    try:
        return User.query.get(user_id)
    except SQLAlchemyError as e:
        print(f"Error fetching user by ID {user_id}: {e}")
        return None


def get_user_by_email(email):
    """
    Lấy một người dùng theo email.
    :param email: Email của người dùng.
    :return: Đối tượng User hoặc None nếu không tìm thấy.
    """
    try:
        return User.query.filter_by(email=email).first()
    except SQLAlchemyError as e:
        print(f"Error fetching user by email {email}: {e}")
        return None


def add_user(name, email, password, role_str="customer"):
    """
    Thêm một người dùng mới vào cơ sở dữ liệu.
    :param name: Tên người dùng.
    :param email: Email người dùng (duy nhất).
    :param password: Mật khẩu chưa mã hóa.
    :param role_str: Chuỗi vai trò ('customer', 'owner', 'admin').
    :return: Đối tượng User đã được thêm hoặc None nếu có lỗi.
    """
    try:
        # Kiểm tra xem email đã tồn tại chưa
        if get_user_by_email(email):
            print(f"User with email {email} already exists.")
            return None

        # Chuyển đổi chuỗi vai trò thành Enum
        try:
            role = UserRole[role_str.upper()]
        except KeyError:
            print(f"Invalid role: {role_str}. Defaulting to CUSTOMER.")
            role = UserRole.CUSTOMER

        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)  # Hash và gán mật khẩu

        db.session.add(new_user)
        db.session.commit()
        return new_user
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error adding user: {e}")
        return None


def update_user(user_id, **kwargs):
    """
    Cập nhật thông tin của một người dùng.
    :param user_id: ID của người dùng cần cập nhật.
    :param kwargs: Từ điển chứa các trường cần cập nhật (name, email, password, role_str).
    :return: True nếu cập nhật thành công, False nếu không tìm thấy người dùng hoặc có lỗi.
    """
    try:
        user = get_user_by_id(user_id)
        if not user:
            print(f"User with ID {user_id} not found for update.")
            return False

        if 'name' in kwargs:
            user.name = kwargs['name']
        if 'email' in kwargs:
            # Kiểm tra email mới có bị trùng với người dùng khác không
            existing_user_with_email = get_user_by_email(kwargs['email'])
            if existing_user_with_email and existing_user_with_email.id != user_id:
                print(f"Email {kwargs['email']} already used by another user.")
                return False
            user.email = kwargs['email']
        if 'password' in kwargs and kwargs['password']:
            user.set_password(kwargs['password'])  # Hash và gán mật khẩu mới
        if 'role_str' in kwargs:
            try:
                user.role = UserRole[kwargs['role_str'].upper()]
            except KeyError:
                print(f"Invalid role: {kwargs['role_str']}. Role not updated.")

        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error updating user {user_id}: {e}")
        return False


def delete_user(user_id):
    """
    Xóa một người dùng khỏi cơ sở dữ liệu.
    :param user_id: ID của người dùng cần xóa.
    :return: True nếu xóa thành công, False nếu không tìm thấy người dùng hoặc có lỗi.
    """
    try:
        user = get_user_by_id(user_id)
        if not user:
            print(f"User with ID {user_id} not found for deletion.")
            return False

        db.session.delete(user)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting user {user_id}: {e}")
        return False

# OrderingFoodApp/dao/user_dao.py
# ... (các imports và hàm hiện có) ...

def count_users_by_role(role=None):
    """
    Đếm tổng số người dùng hoặc số người dùng theo vai trò cụ thể.
    Args:
        role (UserRole, optional): Vai trò cần đếm. Nếu None, đếm tất cả người dùng.
    Returns:
        int: Tổng số người dùng.
    """
    try:
        query = db.session.query(User)
        if role:
            query = query.filter_by(role=role)
        return query.count()
    except SQLAlchemyError as e:
        print(f"Error counting users by role: {e}")
        return 0 # Trả về 0 nếu có lỗi
