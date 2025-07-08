--liquibase formatted sql

--changeset your.name:2
CREATE TABLE db1.test_table1 (test_id INT NOT NULL, test_column INT, PRIMARY KEY (test_id) NOT ENFORCED)