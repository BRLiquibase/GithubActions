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

sql_all = get_all_sql(changes).lower()
reserved = set(["select","from","where","group","order","user","table","index","key","constraint","default","primary","foreign","references","trigger","view","function","procedure","grant","revoke"])
violations = []
for m in re.finditer(r"\bcreate\s+table\s+([\w\"`]+)\b", sql_all):
    name = m.group(1).strip('"`')
    if name in reserved:
        violations.append(f"table '{name}' is reserved")
for m in re.finditer(r"\badd\s+column\s+([\w\"`]+)\b", sql_all):
    name = m.group(1).strip('"`')
    if name in reserved:
        violations.append(f"column '{name}' is reserved")
if violations:
    end_fail("Reserved keywords used as identifiers: " + "; ".join(violations))
else:
    end_ok("No obvious reserved keywords used as identifiers.")
