# 🍽️ **ONLINE FOOD ORDERING SYSTEM**
**Web Application – Software Project Management**

---

## 📌 **Introduction**
The **Online Food Ordering System** is developed to provide a fast and convenient platform for customers to order food, support restaurant owners with menu and order management, and supply an advanced control panel for system administrators.

This project is part of the **Software Project Management** course, developed by a student team from **Ho Chi Minh City Open University**.

---

## 🚀 **Key Features**

### 👤 **Customer**
- **Register / Login** (Email & Google API)
- **Search restaurants by:**
  - Name
  - Category
  - Location (< 10km)
  - Advanced filters (price, rating, cuisine type, etc.)
- **View restaurant details & menu**
- **Shopping cart:**
  - Add items  
  - Update quantity  
  - Remove items  
  - Real-time total calculation  
- **Place order** with payment options:
  - Cash on Delivery (COD)
  - Momo
  - VNPay
- **Apply discount codes**
- **Track order status** (Email + SMS)
- **View order history**
- **Rate & review** completed orders

---

### 🍳 **Restaurant Owner**
- **Manage restaurant profile**
- **Manage menu items:**
  - Add / Edit / Delete dishes
  - Update status (available / sold out)
- **Manage incoming orders:**
  - Confirm  
  - Preparing  
  - Completed  
  - Cancel  
- **Revenue statistics**
- **Manage restaurant-specific discount codes**
- **Respond to customer reviews**

---

### 🛠️ **Admin**
- **User management**
- **Restaurant management** (review registration / CRUD)
- **Promotion management** (system-wide)
- **Statistics dashboard:**
  - User statistics  
  - Restaurant statistics  
  - Promotion usage statistics  

---

## 🧱 **Architecture & Technologies**

### 🖥️ **Backend**
- Python (Flask)  
- SQLAlchemy ORM  
- RESTful API  
- API Testing: Postman, Pytest  

### 🗄️ **Database**
- MySQL  
- Schema includes: **User, Restaurant, MenuItem, Order, OrderItem, Promotion, Review,...**

### 🎨 **Frontend**
- HTML / CSS / Bootstrap 5  
- Jinja2 Template Engine  

### 📦 **DevOps**
- GitHub (version control)  
- CI/CD using Jenkins / GitHub Actions  
- Deployment on PythonAnywhere  

---

## 📂 **Suggested Folder Structure**

```bash
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

---

## ⚙️ **Installation & Setup**

### **1️⃣ Clone the repository**
```bash
git clone <repository_link>
cd <project_folder>
2️⃣ Create virtual environment
bash
Sao chép mã
python -m venv venv
venv/Scripts/activate      # Windows
source venv/bin/activate   # Mac/Linux
3️⃣ Install dependencies
bash
Sao chép mã
pip install -r requirements.txt
4️⃣ Configure database
Create a MySQL database

Update credentials in config.py

5️⃣ Run the application
bash
Sao chép mã
python app.py
➡️ Access at: http://localhost:5000

📊 Development Process (Agile – Scrum)
🔥 Sprint 1 – Core Features
Requirement analysis

System design (Use Case, Activity, Sequence Diagrams)

Database & UI design

Implementation:

✔ Restaurant search & browse

✔ Menu display & add to cart

✔ Shopping cart

✔ Place order (COD)

✔ Basic restaurant owner features

✔ Basic admin features

⚡ Sprint 2 – Advanced Features
Online payment: Momo, VNPay

Email & SMS notifications

Advanced search filters + Map API

Order rating & reviews

Revenue statistics

UI/UX enhancements

🧪 Testing
Unit testing with Pytest

API testing using Postman

Integration testing via Jenkins pipeline

📈 Project Evaluation
Completed according to Gantt Chart timeline

Core functions operate stably

Fully functional CI/CD pipeline

All goals defined in the Project Charter achieved

👥 Team Members
bash
Sao chép mã
Student ID     Name                 Role
2254052042     Bùi Dạ Lý            Backend, Database
2254052008     Võ Thị Ngọc Chi      Frontend, Requirements Analysis
2254050009     Huỳnh Lệ Giang       Testing, UI/UX
2254052031     Võ Tấn Huy           Backend, API, Admin Features
