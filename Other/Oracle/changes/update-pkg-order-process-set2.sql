-- Sample updated package body for PKG_ORDER_PROCESS (Set 2)

CREATE OR REPLACE PACKAGE BODY PKG_ORDER_PROCESS AS

  PROCEDURE create_order(p_order_id IN NUMBER) IS
  BEGIN
    INSERT INTO ORDER_AUDIT_LOG (audit_id, order_id, action, created_at)
    VALUES (ORDER_AUDIT_SEQ.NEXTVAL, p_order_id, 'CREATED', SYSTIMESTAMP);
    
    DBMS_OUTPUT.PUT_LINE('Order created successfully. [v2]');
  END;

END PKG_ORDER_PROCESS;
