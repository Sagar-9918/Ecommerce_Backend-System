-- ============================================
--   E-COMMERCE DATABASE SCHEMA
--   Amazon-like Architecture
-- ============================================

CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

-- ─────────────────────────────────────────
-- USERS TABLE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)        NOT NULL,
    email       VARCHAR(150)        NOT NULL UNIQUE,
    password    VARCHAR(255)        NOT NULL,      -- bcrypt hashed
    role        ENUM('customer','admin') DEFAULT 'customer',
    created_at  TIMESTAMP           DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP           DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_email (email)
);

-- ─────────────────────────────────────────
-- CATEGORIES TABLE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- PRODUCTS TABLE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(200)   NOT NULL,
    description  TEXT,
    price        DECIMAL(10,2)  NOT NULL,
    stock        INT            NOT NULL DEFAULT 0,
    category_id  INT,
    image_url    VARCHAR(500),
    is_active    BOOLEAN        DEFAULT TRUE,
    created_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,

    -- Optimized indexes for frequent queries
    INDEX idx_category    (category_id),
    INDEX idx_price       (price),
    INDEX idx_active      (is_active),
    INDEX idx_name        (name),
    FULLTEXT INDEX idx_search (name, description)   -- Full-text search
);

-- ─────────────────────────────────────────
-- CART TABLE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cart (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT  NOT NULL,
    product_id  INT  NOT NULL,
    quantity    INT  NOT NULL DEFAULT 1,
    added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,

    UNIQUE KEY unique_cart_item (user_id, product_id),
    INDEX idx_user_cart (user_id)
);

-- ─────────────────────────────────────────
-- ORDERS TABLE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT            NOT NULL,
    total_amount    DECIMAL(10,2)  NOT NULL,
    status          ENUM('pending','confirmed','shipped','delivered','cancelled')
                    DEFAULT 'pending',
    shipping_address TEXT          NOT NULL,
    payment_method  VARCHAR(50)    DEFAULT 'COD',
    created_at      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    INDEX idx_user_orders  (user_id),
    INDEX idx_order_status (status),
    INDEX idx_created_at   (created_at)
);

-- ─────────────────────────────────────────
-- ORDER ITEMS TABLE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    order_id    INT            NOT NULL,
    product_id  INT            NOT NULL,
    quantity    INT            NOT NULL,
    unit_price  DECIMAL(10,2)  NOT NULL,   -- price at time of purchase (snapshot)

    FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,

    INDEX idx_order_items (order_id)
);

-- ─────────────────────────────────────────
-- SEED DATA
-- ─────────────────────────────────────────
INSERT INTO categories (name, description) VALUES
    ('Electronics',   'Gadgets and electronic devices'),
    ('Books',         'Fiction, non-fiction, and textbooks'),
    ('Clothing',      'Apparel and accessories'),
    ('Home & Kitchen','Home appliances and kitchenware'),
    ('Sports',        'Sports and outdoor equipment');

-- Admin user (password: admin123)
INSERT INTO users (name, email, password, role) VALUES
    ('Admin User', 'admin@shop.com',
     '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin');

INSERT INTO products (name, description, price, stock, category_id, image_url) VALUES
    ('iPhone 15 Pro',       'Latest Apple smartphone with A17 chip',  99999.00, 50,  1, 'https://example.com/iphone15.jpg'),
    ('Samsung Galaxy S24',  'Flagship Android phone by Samsung',       79999.00, 75,  1, 'https://example.com/s24.jpg'),
    ('Clean Code',          'A Handbook of Agile Software by R.Martin',  599.00, 200, 2, 'https://example.com/cleancode.jpg'),
    ('Levi''s 501 Jeans',   'Classic straight-fit denim jeans',         3499.00, 150, 3, 'https://example.com/levis.jpg'),
    ('Instant Pot Duo',     '7-in-1 electric pressure cooker',          7999.00, 80,  4, 'https://example.com/instantpot.jpg'),
    ('Nike Running Shoes',  'Lightweight running shoes for athletes',   5999.00, 100, 5, 'https://example.com/nike.jpg'),
    ('MacBook Air M2',      'Apple laptop with M2 chip, 8GB RAM',     114999.00, 30,  1, 'https://example.com/macbook.jpg'),
    ('The Alchemist',       'Paulo Coelho bestselling novel',            299.00, 500, 2, 'https://example.com/alchemist.jpg');
