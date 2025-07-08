--liquibase formatted sql

--changeset briley:ddl_create_table_organizations labels:release-1.0.0
CREATE TABLE ORGANIZATIONS (
    ID NUMBER PRIMARY KEY,
    NAME VARCHAR2(200),
    INDUSTRY VARCHAR2(400),
    EMPLOYEE_COUNT NUMBER
);  
--rollback DROP TABLE ORGANIZATIONS;