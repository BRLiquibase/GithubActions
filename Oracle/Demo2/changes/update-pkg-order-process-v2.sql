-- Updated version of PKG_ORDER_PROCESS (v2)

CREATE OR REPLACE PACKAGE BODY PKG_ORDER_PROCESS AS

  PROCEDURE create_order(p_order_id IN NUMBER) IS
  BEGIN
    INSERT INTO ORDER_AUDIT_LOG (audit_id, order_id, action, created_at)
    VALUES (ORDER_AUDIT_SEQ.NEXTVAL, p_order_id, 'ORDER_CREATED_V2', SYSTIMESTAMP);

    DBMS_OUTPUT.PUT_LINE('Order created by version 2 logic.');
  END;

END PKG_ORDER_PROCESS;
/
