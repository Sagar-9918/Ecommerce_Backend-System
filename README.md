# 🛒 E-Commerce Backend System
> Backend API built with Python Flask + MySQL

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![MySQL](https://img.shields.io/badge/MySQL-8.x-orange)
![JWT](https://img.shields.io/badge/Auth-JWT-red)

---

## 📌 About The Project

A fully functional e-commerce backend system with product listing, cart management, and order processing — built using a clean **layered architecture** (Routes → Services → Models).

---

## 📁 Project Structure

```
ecommerce/
├── app.py                    ← Entry point
├── config.py                 ← Configuration
├── requirements.txt          ← Dependencies
├── .env.example              ← Environment template
│
├── database/
│   └── schema.sql            ← DB schema + seed data
│
├── models/                   ← Data Layer (OOP)
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   └── order.py
│
├── services/                 ← Business Logic Layer
│   ├── auth_service.py
│   ├── product_service.py
│   ├── cart_service.py
│   └── order_service.py
│
├── routes/                   ← API Layer
│   ├── auth_routes.py
│   ├── product_routes.py
│   ├── cart_routes.py
│   └── order_routes.py
│
└── utils/                    ← Shared Utilities
    ├── db.py
    ├── jwt_handler.py
    └── response.py
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Sagar-9918/ecommerce-backend.git
cd ecommerce-backend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
```
Open `.env` and fill in your MySQL password and secret keys.

### 4. Set up the database
```bash
mysql -u root -p < database/schema.sql
```
Or open `database/schema.sql` in MySQL Workbench and run it.

### 5. Run the server
```bash
python app.py
```

Server runs at → **http://localhost:5000**

---

## 🌐 API Endpoints

### 🔐 Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login & get token |
| POST | /auth/refresh | Refresh token |
| GET | /auth/profile | Get my profile |
| PUT | /auth/profile | Update profile |
| PUT | /auth/change-password | Change password |

### 📦 Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /products/ | List all products |
| GET | /products/<id> | Product detail |
| GET | /products/categories | All categories |
| POST | /products/ | Create product (admin) |
| PUT | /products/<id> | Update product (admin) |
| DELETE | /products/<id> | Delete product (admin) |

### 🛒 Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /cart/ | View cart |
| POST | /cart/ | Add item |
| PUT | /cart/<product_id> | Update quantity |
| DELETE | /cart/<product_id> | Remove item |
| DELETE | /cart/ | Clear cart |

### 📋 Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /orders/ | Place order |
| GET | /orders/ | My orders |
| GET | /orders/<id> | Order detail |
| PUT | /orders/<id>/cancel | Cancel order |
| GET | /orders/admin | All orders (admin) |
| PUT | /orders/admin/<id>/status | Update status (admin) |

---

## 🔑 Default Admin Account
```
Email    : admin@shop.com
Password : admin123
```

---

## 🏗️ Architecture

```
Request → Routes → Services → Models → MySQL → Response
```

- **Routes** — Handle HTTP requests/responses
- **Services** — Business logic and validations
- **Models** — Database operations using OOP
- **Utils** — Shared helpers (JWT, DB, Response)

---

## 🛡️ Security Features

- Passwords hashed with **bcrypt**
- **JWT** access tokens (1hr) + refresh tokens (7 days)
- SQL injection prevention via **parameterised queries**
- Role-based access control **(RBAC)**

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Framework | Flask 3.0 |
| Database | MySQL 8.x |
| Auth | JWT (PyJWT) |
| Hashing | bcrypt |
| DB Driver | mysql-connector-python |
