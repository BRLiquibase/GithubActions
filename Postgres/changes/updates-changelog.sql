--changeset briley:5 labels:release-1.0.0 context:dev
-- Creates the 'downloads' table to log downloadable content access by customers, including file name and timestamp.
CREATE TABLE downloads_1 (
  download_id SERIAL PRIMARY KEY,
  customer_id INT,
  download_date TIMESTAMP,
  file_name VARCHAR(255),
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

--rollback DROP TABLE downloads;