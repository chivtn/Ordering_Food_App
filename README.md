🍽️ ONLINE FOOD ORDERING SYSTEM

Web Application – Software Project Management

📌 Introduction

The Online Food Ordering System is developed to provide a fast and convenient platform for customers to order food, support restaurant owners in managing their menu and orders, and offer a powerful control panel for system administrators.

This project is part of the Software Project Management course, developed by a student team from Ho Chi Minh City Open University.

🚀 Key Features
👤 Customer

Register / Login (Email & Google API)

Search restaurants by:

Name

Category

Location (< 10km)

Advanced filters (price, rating, cuisine type, etc.)

View restaurant details and menu

Shopping cart:

Add, update quantity, remove items

Real-time total amount calculation

Place order + payment options:

Cash on Delivery (COD)

Momo

VNPay

Apply discount codes

Track order status (Email + SMS notifications)

View order history

Rate and review completed orders

🍳 Restaurant Owner

Manage restaurant information

Manage menu items:

Add / edit / delete dishes

Update item status (available / sold out)

Manage incoming orders:

Confirm

Preparing

Completed

Cancel

Revenue statistics

Manage restaurant-specific discount codes

Reply to customer reviews

🛠️ Admin

User management

Restaurant management (review registration / CRUD)

System-wide promotion code management

Statistics dashboard:

User statistics

Restaurant statistics

Promotion usage statistics

🧱 Architecture & Technologies
🖥️ Backend

Python (Flask)

SQLAlchemy ORM

RESTful API

API Testing: Postman, Pytest

🗄️ Database

MySQL

Schema includes: User, Restaurant, MenuItem, Order, OrderItem, Promotion, Review,...

🎨 Frontend

HTML / CSS / Bootstrap 5

Jinja2 Template Engine

📦 DevOps

GitHub (version control)

CI/CD using Jenkins / GitHub Actions

Deployment on PythonAnywhere

📂 Suggested Folder Structure
📦 project
├── app.py
├── config.py
├── /static
│   ├── css
│   ├── js
│   └── images
├── /templates
│   ├── customer
│   ├── restaurant
│   └── admin
├── /models
├── /routes
├── /services
└── /utils

⚙️ Installation & Setup
1️⃣ Clone the repository
git clone <repository_link>
cd <project_folder>

2️⃣ Create virtual environment
python -m venv venv
venv/Scripts/activate      # Windows
source venv/bin/activate   # Mac / Linux

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure database

Create a MySQL database

Update DB credentials in config.py

5️⃣ Run the application
python app.py


Access the application at http://localhost:5000/

📊 Development Process (Agile – Scrum)

The project includes 2 Sprints, each lasting about ~2 weeks.

🔥 Sprint 1 – Core Features

Requirement analysis

System design (Use Case, Activity, Sequence Diagrams)

Database schema + UI design

Implement main features:
✔ Restaurant search & browse
✔ Menu display & add to cart
✔ Shopping cart
✔ Place order (COD)
✔ Basic restaurant owner features
✔ Basic admin features

⚡ Sprint 2 – Advanced Features

Online payment integration (Momo, VNPay)

Email & SMS notifications

Advanced search filters + Map API

Order rating & reviews

Revenue statistics

UI/UX improvements

🧪 Testing

Unit testing with Pytest

API testing with Postman

Integration testing via Jenkins pipeline

📈 Project Evaluation

Completed according to planned schedule (Gantt Chart)

All major functions operate stably

CI/CD pipeline successfully configured

Fully met goals defined in the Project Charter

👥 Team Members
Student ID	Name	Role
2254052042	Bùi Dạ Lý	Backend, Database
2254052008	Võ Thị Ngọc Chi	Frontend, Requirements Analysis
2254050009	Huỳnh Lệ Giang	Testing, UI/UX
2254052031	Võ Tấn Huy	Backend, API, Admin Features
