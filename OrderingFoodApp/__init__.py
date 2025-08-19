# OrderingFoodApp/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
####
from flask_mail import Mail  # Thêm import Flask-Mail
import os

# Load biến môi trường từ .env
load_dotenv()

# Khởi tạo extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
####
mail = Mail()  # Khởi tạo Flask-Mail


def init_app():
    """
    Khởi tạo Flask App, tích hợp các extension
    """
    app = Flask(__name__)



    # ====== CONFIGURATION ======
    from OrderingFoodApp.config import Config
    app.config.from_object(Config)

    # ====== CẤU HÌNH EMAIL (GMAIL SMTP) ======
    app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
    app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True") == "True"
    app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL", "False") == "True"
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

    # ====== INITIALIZE EXTENSIONS ======
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from OrderingFoodApp.models import User, UserRole
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    app.jinja_env.globals['UserRole'] = UserRole

    # ====== IMPORT MODELS ======
    from OrderingFoodApp import models

    # ====== REGISTER BLUEPRINTS ======
    from OrderingFoodApp.routes.auth import auth_bp
    from OrderingFoodApp.routes.customer import customer_bp
    from OrderingFoodApp.routes.owner import owner_bp
    from OrderingFoodApp.routes.admin import admin_bp
    from OrderingFoodApp.routes.home import home_bp
    from OrderingFoodApp.routes.profile import profile_bp
    from OrderingFoodApp.routes import payment

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(profile_bp)

    # Khởi tạo Flask-Mail
    mail.init_app(app)

    return app
