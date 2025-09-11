# Liquibase Custom Policy Check (Python)
# This script is intended to be used with Liquibase Pro custom policy checks.
# It examines the SQL generated for the current changeset and optionally the database snapshot.
# If the check detects a violation, it should set status.fired = True, populate a message,
# and exit(1). Otherwise exit(0).

import sys
import re
try:
    import sqlparse  # Provided by Liquibase's embedded environment
except Exception:
    sqlparse = None

import liquibase_utilities
import liquibase_database
import liquibase_json

status = liquibase_utilities.get_status()
logger = liquibase_utilities.get_logger()
changeset = liquibase_utilities.get_changeset()
changes = liquibase_utilities.get_changes()

def get_all_sql(changes):
    sql_parts = []
    for ch in changes:
        try:
            sql = liquibase_utilities.generate_sql(ch) or ""
        except Exception as e:
            sql = ""
        if sql:
            try:
                sql = liquibase_utilities.strip_comments(sql)
            except Exception:
                pass
            sql_parts.append(sql)
    return "\n".join(sql_parts)

def end_ok(msg="OK"):
    status.fired = False
    status.message = msg
    sys.exit(0)

def end_fail(msg):
    status.fired = True
    status.message = msg
    sys.exit(1)

sql = get_all_sql(changes).lower()
db = liquibase_utilities.get_database()
try:
    db_short = liquibase_database.get_short_name(db)
except Exception:
    db_short = ""
if db_short == "postgresql":
    if " public." in sql or re.search(r"set\s+search_path[\s=]+public", sql):
        end_fail("PostgreSQL policy: avoid using the 'public' schema.")
end_ok("No 'public' schema usage detected (or not PostgreSQL).")
