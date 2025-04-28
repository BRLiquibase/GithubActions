-- Create customers table (QA has qa_flagged column)
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    qa_flagged BOOLEAN DEFAULT false
);

-- Create addresses table
CREATE TABLE IF NOT EXISTS addresses (
    address_id SERIAL PRIMARY KEY,
    customer_id INT,
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create rental_history table
CREATE TABLE IF NOT EXISTS rental_history (
    rental_id SERIAL PRIMARY KEY,
    customer_id INT,
    rental_date DATE,
    return_date DATE,
    rental_amount DECIMAL(10, 2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Insert into customers
INSERT INTO customers (first_name, last_name, email, phone_number, qa_flagged) VALUES
('Alice', 'Johnson', 'alice.j@example.com', '555-1234', false),
('Bob', 'Smith', 'bob.smith@example.com', '555-5678', true),
('Charlie', 'Lee', 'charlie.lee@example.com', '555-9012', false);

-- Insert into addresses
INSERT INTO addresses (customer_id, address_line1, address_line2, city, state, zip_code) VALUES
(1, '123 Main St', NULL, 'Springfield', 'IL', '62704'),
(2, '456 Elm St', 'Apt 2B', 'Chicago', 'IL', '60616'),
(3, '789 Oak St', NULL, 'Naperville', 'IL', '60540');

-- Insert into rental_history
INSERT INTO rental_history (customer_id, rental_date, return_date, rental_amount) VALUES
(1, '2024-01-10', '2024-01-12', 9.99),
(2, '2024-02-15', '2024-02-18', 14.50),
(3, '2024-03-01', '2024-03-03', 7.75);
