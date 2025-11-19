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
