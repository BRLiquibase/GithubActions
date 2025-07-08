--liquibase formatted sql

--changeset david:create_users_table labels:ddl,users
CREATE TABLE db1.user_roles (
    user_id STRING NOT NULL,
    user_name STRING,
    email STRING,
    signup_date DATE,
    is_active BOOLEAN,
    PRIMARY KEY (user_id) NOT ENFORCED
)
USING DELTA
COMMENT 'User account information'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
);

--changeset briley:create_products_table labels:ddl,products
CREATE TABLE db1.products (
    product_id STRING NOT NULL,
    product_name STRING NOT NULL,
    category STRING,
    price DECIMAL(10,2),
    in_stock BOOLEAN,
    created_at TIMESTAMP,
    PRIMARY KEY (product_id) NOT ENFORCED
)
USING DELTA
COMMENT 'Product catalog with pricing and inventory status';

--changeset briley:create_orders_table labels:ddl,orders
CREATE TABLE db1.orders (
    order_id STRING NOT NULL,
    user_id STRING NOT NULL,
    product_id STRING NOT NULL,
    quantity INT,
    total_amount DECIMAL(12,2),
    order_timestamp TIMESTAMP,
    PRIMARY KEY (order_id) NOT ENFORCED
)
USING DELTA
PARTITIONED BY (order_timestamp)
COMMENT 'Order transactions including user and product info';
