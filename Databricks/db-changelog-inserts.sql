--liquibase formatted sql

--changeset briley:insert_initial_users labels:dml,users
INSERT INTO db1.users (user_id, user_name, email, signup_date, is_active) VALUES
('u001', 'Alice Smith', 'alice@example.com', DATE('2023-01-15'), true),
('u002', 'Bob Johnson', 'bob@example.com', DATE('2023-02-20'), true);

--changeset briley:insert_initial_products labels:dml,products
INSERT INTO db1.products (product_id, product_name, category, price, in_stock, created_at) VALUES
('p001', 'Wireless Mouse', 'Electronics', 25.99, true, CURRENT_TIMESTAMP()),
('p002', 'Notebook', 'Stationery', 3.49, true, CURRENT_TIMESTAMP());

--changeset briley:insert_sample_orders labels:dml,orders
INSERT INTO db1.orders (order_id, user_id, product_id, quantity, total_amount, order_timestamp) VALUES
('o1001', 'u001', 'p001', 2, 51.98, CURRENT_TIMESTAMP()),
('o1002', 'u002', 'p002', 5, 17.45, CURRENT_TIMESTAMP());
