import pytest
from OrderingFoodApp.dao import restaurants_owner as dao
from OrderingFoodApp.models import db, User, Restaurant, UserRole, RestaurantApprovalStatus
@pytest.fixture
def seed_restaurant_data(app):
    with app.app_context():
        owner = User(name="Owner", email="o@test.com", password="pass", role=UserRole.OWNER)
        db.session.add(owner)
        db.session.commit()

        restaurant = Restaurant(owner_id=owner.id, name="Test R", approval_status=RestaurantApprovalStatus.APPROVED)
        db.session.add(restaurant)
        db.session.commit()

        # Chỉ trả về ID để tránh DetachedInstanceError
        return {
            "owner_id": owner.id,
            "restaurant_id": restaurant.id
        }


def test_get_restaurants_by_owner(app, seed_restaurant_data):
    with app.app_context():
        res = dao.RestaurantDAO.get_restaurants_by_owner(seed_restaurant_data["owner_id"])
        assert len(res) == 1
        assert res[0].name == "Test R"
