import pytest
from OrderingFoodApp.models import db, User, Restaurant, MenuCategory, MenuItem, UserRole, RestaurantApprovalStatus
from OrderingFoodApp.dao.menu_owner import MenuDAO


@pytest.fixture
def seed_menu_data_for_errors(app):
    """Tạo dữ liệu mẫu cho test lỗi menu"""
    with app.app_context():
        owner = User(name="Owner", email="owner@test.com", password="pass", role=UserRole.OWNER)
        db.session.add(owner)
        db.session.commit()

        restaurant = Restaurant(
            owner_id=owner.id,
            name="Test R",
            approval_status=RestaurantApprovalStatus.APPROVED
        )
        db.session.add(restaurant)
        db.session.commit()

        category = MenuCategory(name="Drinks")
        db.session.add(category)
        db.session.commit()

        item = MenuItem(
            name="Coffee",
            restaurant_id=restaurant.id,
            category_id=category.id,
            price=2.5
        )
        db.session.add(item)
        db.session.commit()

        return {
            "owner_id": owner.id,
            "restaurant_id": restaurant.id,
            "category_id": category.id,
            "item_id": item.id
        }


def test_get_menu_items_invalid_restaurant(app):
    """Truy vấn menu khi nhà hàng không tồn tại -> trả None"""
    with app.app_context():
        result = MenuDAO.get_menu_items(restaurant_id=999)
        assert result is None


def test_get_menu_items_not_approved_restaurant(app):
    """Truy vấn menu khi nhà hàng chưa được duyệt -> trả None"""
    with app.app_context():
        # Tạo owner để tránh lỗi FK
        owner = User(name="Owner Pending", email="owner_pending@test.com", password="pass", role=UserRole.OWNER)
        db.session.add(owner)
        db.session.commit()

        rest = Restaurant(
            name="R1",
            owner_id=owner.id,
            approval_status=RestaurantApprovalStatus.PENDING
        )
        db.session.add(rest)
        db.session.commit()

        result = MenuDAO.get_menu_items(restaurant_id=rest.id)
        assert result is None


def test_create_menu_item_invalid_restaurant(app):
    """Tạo menu khi nhà hàng không tồn tại -> None"""
    with app.app_context():
        result = MenuDAO.create_menu_item(
            restaurant_id=999,
            category_id=1,
            name="Test",
            description="desc",
            price=10
        )
        assert result is None


def test_update_menu_item_not_found(app):
    """Cập nhật menu item không tồn tại -> None"""
    with app.app_context():
        result = MenuDAO.update_menu_item(item_id=999, name="Updated")
        assert result is None


def test_delete_menu_item_not_found(app):
    """Xóa menu item không tồn tại -> False"""
    with app.app_context():
        result = MenuDAO.delete_menu_item(item_id=999)
        assert result is False


def test_toggle_menu_item_not_found(app):
    """Đổi trạng thái menu item không tồn tại -> False"""
    with app.app_context():
        result = MenuDAO.toggle_menu_item_status(item_id=999)
        assert result is False
