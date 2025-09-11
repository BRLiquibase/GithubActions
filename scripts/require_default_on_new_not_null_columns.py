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
violations = []
for m in re.finditer(r"\balter\s+table\s+[\w\.\"]+\s+add\s+column\s+([\w\"]+)\s+([\w\(\)\,\s]+?)\s*(,|;)", sql_all):
    col = m.group(1).strip('"`')
    tail = m.group(2)
    if re.search(r"\bnot\s+null\b", tail) and not re.search(r"\bdefault\b", tail):
        violations.append(col)
if violations:
    end_fail("NOT NULL columns added without DEFAULT: " + ", ".join(violations))
else:
    end_ok("All new NOT NULL columns have DEFAULTs (or none were added).")
