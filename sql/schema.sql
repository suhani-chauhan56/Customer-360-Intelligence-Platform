-- Customer 360 Intelligence Platform
-- MySQL 8.0+ warehouse schema. Running this file rebuilds the project tables.

CREATE DATABASE IF NOT EXISTS customer360_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE customer360_db;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS fact_campaign;
DROP TABLE IF EXISTS fact_product_reviews;
DROP TABLE IF EXISTS fact_customer_reviews;
DROP TABLE IF EXISTS fact_web_activity;
DROP TABLE IF EXISTS fact_payments;
DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS dim_campaign;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;
SET FOREIGN_KEY_CHECKS = 1;

-- One row per Olist customer_unique_id. This is the canonical Customer 360 key.
CREATE TABLE dim_customer (
    customer_id VARCHAR(100) PRIMARY KEY,
    city VARCHAR(100),
    state VARCHAR(10),
    zip_code_prefix INT,
    source_customer_count INT NOT NULL DEFAULT 1,
    INDEX idx_customer_state_city (state, city)
) ENGINE=InnoDB;

CREATE TABLE dim_product (
    product_id VARCHAR(100) PRIMARY KEY,
    category_name VARCHAR(150),
    category_name_english VARCHAR(150),
    product_weight_g DECIMAL(12, 2),
    product_length_cm DECIMAL(12, 2),
    product_height_cm DECIMAL(12, 2),
    product_width_cm DECIMAL(12, 2),
    INDEX idx_product_category (category_name_english)
) ENGINE=InnoDB;

CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    calendar_year SMALLINT NOT NULL,
    calendar_quarter TINYINT NOT NULL,
    month_number TINYINT NOT NULL,
    month_name VARCHAR(12) NOT NULL,
    week_number TINYINT NOT NULL,
    day_of_month TINYINT NOT NULL,
    day_name VARCHAR(12) NOT NULL,
    is_weekend TINYINT(1) NOT NULL
) ENGINE=InnoDB;

-- One row per Olist order item. Revenue excludes freight; gross_value includes it.
CREATE TABLE fact_orders (
    order_id VARCHAR(100) NOT NULL,
    order_item_id INT NOT NULL,
    source_customer_id VARCHAR(100) NOT NULL,
    customer_id VARCHAR(100) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    seller_id VARCHAR(100),
    order_status VARCHAR(50),
    purchase_date DATETIME NOT NULL,
    purchase_date_key INT NOT NULL,
    delivered_date DATETIME NULL,
    estimated_delivery_date DATETIME NULL,
    quantity INT NOT NULL DEFAULT 1,
    item_price DECIMAL(12, 2) NOT NULL,
    freight_value DECIMAL(12, 2) NOT NULL,
    revenue DECIMAL(12, 2) NOT NULL,
    gross_value DECIMAL(12, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id),
    INDEX idx_orders_customer_date (customer_id, purchase_date),
    INDEX idx_orders_product (product_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    CONSTRAINT fk_orders_product FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    CONSTRAINT fk_orders_date FOREIGN KEY (purchase_date_key) REFERENCES dim_date(date_key)
) ENGINE=InnoDB;

CREATE TABLE fact_payments (
    order_id VARCHAR(100) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(50),
    payment_installments INT,
    payment_value DECIMAL(12, 2),
    PRIMARY KEY (order_id, payment_sequential),
    INDEX idx_payments_type (payment_type)
) ENGINE=InnoDB;

-- Simulated identity links are clearly marked and are used only for behavior features.
CREATE TABLE fact_web_activity (
    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    click_user_id VARCHAR(100) NOT NULL,
    event_time DATETIME NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    source_product_id VARCHAR(100),
    category_code VARCHAR(200),
    brand VARCHAR(100),
    price DECIMAL(12, 2),
    user_session VARCHAR(100),
    identity_link_is_simulated TINYINT(1) NOT NULL DEFAULT 1,
    INDEX idx_web_customer_time (customer_id, event_time),
    INDEX idx_web_event_type (event_type),
    CONSTRAINT fk_web_customer FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
) ENGINE=InnoDB;

-- Olist feedback can be connected to the canonical Olist customer through order_id.
CREATE TABLE fact_customer_reviews (
    review_id VARCHAR(120) NOT NULL,
    order_id VARCHAR(100) NOT NULL,
    customer_id VARCHAR(100) NOT NULL,
    review_date DATETIME NULL,
    rating TINYINT,
    review_title TEXT,
    review_text TEXT,
    PRIMARY KEY (review_id, order_id),
    INDEX idx_customer_reviews_customer (customer_id),
    CONSTRAINT fk_customer_reviews_customer FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
) ENGINE=InnoDB;

-- Datafiniti/Amazon is a separate product-intelligence source, never a customer join.
CREATE TABLE fact_product_reviews (
    review_key VARCHAR(64) PRIMARY KEY,
    source_product_id VARCHAR(100),
    product_name VARCHAR(500),
    category_name VARCHAR(150),
    review_date DATETIME NULL,
    rating DECIMAL(4, 2),
    review_text TEXT,
    sentiment_label VARCHAR(30),
    sentiment_score DECIMAL(6, 4),
    INDEX idx_product_reviews_category (category_name)
) ENGINE=InnoDB;

CREATE TABLE dim_campaign (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_type VARCHAR(50) NOT NULL,
    campaign_start_date DATE NOT NULL,
    campaign_cost DECIMAL(14, 2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE fact_campaign (
    campaign_event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    campaign_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(100) NOT NULL,
    email_sent TINYINT(1) NOT NULL,
    opened TINYINT(1) NOT NULL,
    clicked TINYINT(1) NOT NULL,
    converted TINYINT(1) NOT NULL,
    revenue_generated DECIMAL(12, 2) NOT NULL,
    campaign_date DATE NOT NULL,
    is_synthetic TINYINT(1) NOT NULL DEFAULT 1,
    INDEX idx_campaign_customer (customer_id),
    INDEX idx_campaign_id (campaign_id),
    CONSTRAINT fk_campaign_customer FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    CONSTRAINT fk_campaign_dimension FOREIGN KEY (campaign_id) REFERENCES dim_campaign(campaign_id)
) ENGINE=InnoDB;
