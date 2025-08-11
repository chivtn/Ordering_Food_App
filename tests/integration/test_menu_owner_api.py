
import pytest
from OrderingFoodApp.dao import menu_owner as dao
from OrderingFoodApp.models import db, User, Restaurant, MenuCategory, MenuItem, UserRole, RestaurantApprovalStatus

@pytest.fixture
def seed_menu_data(app):
    with app.app_context():
        owner = User(name="Owner", email="owner@test.com", password="pass", role=UserRole.OWNER)
        db.session.add(owner)
        db.session.commit()

        restaurant = Restaurant(owner_id=owner.id, name="Test R", approval_status=RestaurantApprovalStatus.APPROVED)
        db.session.add(restaurant)
        db.session.commit()

        category = MenuCategory(name="Drinks")
        db.session.add(category)
        db.session.commit()

        item = MenuItem(name="Coffee", restaurant_id=restaurant.id, category_id=category.id, price=2.5)
        db.session.add(item)
        db.session.commit()

        # ✅ Trả về ID thay vì object
        return {
            "owner_id": owner.id,
            "restaurant_id": restaurant.id,
            "category_id": category.id,
            "item_id": item.id
        }

def test_get_menu_items_by_restaurant_integration(app, seed_menu_data):
    with app.app_context():
        result = dao.MenuDAO.get_menu_items(seed_menu_data["restaurant_id"])
        assert result.total == 1
        assert result.items[0].name == "Coffee"
