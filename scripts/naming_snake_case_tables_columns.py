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

sql_all = get_all_sql(changes)
violations = []
create_tbl = re.findall(r"(?is)\bcreate\s+table\s+([\w\."]+)\s*\(", sql_all)
add_col = re.findall(r"(?is)\badd\s+column\s+([\w\."]+)\s+", sql_all)
def is_snake(name):
    name = name.split('.')[-1].strip('"`')
    return re.match(r"^[a-z][a-z0-9_]*$", name) is not None
for t in create_tbl:
    if not is_snake(t):
        violations.append(f"table name '{t}' is not snake_case")
for c in add_col:
    if not is_snake(c):
        violations.append(f"column name '{c}' is not snake_case")
if violations:
    end_fail("Naming convention violation(s): " + "; ".join(violations[:5]) + ("" if len(violations)<=5 else f" (+{len(violations)-5} more)"))
else:
    end_ok("All new table/column names appear to be snake_case.")
