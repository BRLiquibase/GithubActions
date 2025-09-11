-- liquibase formatted sql

-- changeset briley:001-create-customers
-- comment: Create customers table
CREATE TABLE IF NOT EXISTS customers (
  id BIGSERIAL PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- rollback DROP TABLE IF EXISTS customers;

-- changeset davidd:002-create-orders
-- comment: Create orders table referencing customers
CREATE TABLE IF NOT EXISTS orders (
  id BIGSERIAL PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  amount NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
  status TEXT NOT NULL DEFAULT 'PENDING',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- rollback DROP TABLE IF EXISTS orders;

-- changeset james:003-add-phone-to-customers
-- comment: Add phone column to customers
ALTER TABLE customers
  ADD COLUMN phone VARCHAR(20);
-- rollback ALTER TABLE customers DROP COLUMN IF EXISTS phone;

-- changeset briley:004-widen-amount-and-add-status-check
-- comment: Widen order amount and add allowable status values
ALTER TABLE orders
  ALTER COLUMN amount TYPE NUMERIC(12,2);
ALTER TABLE orders
  ADD CONSTRAINT orders_status_chk CHECK (status IN ('PENDING','PAID','CANCELLED'));
-- rollback ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_status_chk;
-- rollback ALTER TABLE orders ALTER COLUMN amount TYPE NUMERIC(10,2);

-- changeset davidd:005-add-index-orders-customer-createdat
-- comment: Composite index to speed lookups by customer & recency
CREATE INDEX IF NOT EXISTS idx_orders_customer_created_at
  ON orders (customer_id, created_at DESC);
-- rollback DROP INDEX IF EXISTS idx_orders_customer_created_at;

Drop table addresses;