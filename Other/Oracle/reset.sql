BEGIN
  -- Drop all tables
  FOR t IN (SELECT table_name FROM user_tables) LOOP
    EXECUTE IMMEDIATE 'DROP TABLE "' || t.table_name || '" CASCADE CONSTRAINTS';
  END LOOP;

  -- Drop all packages (spec and body)
  FOR p IN (SELECT object_name FROM user_objects WHERE object_type = 'PACKAGE') LOOP
    EXECUTE IMMEDIATE 'DROP PACKAGE "' || p.object_name || '"';
  END LOOP;
END;
/
