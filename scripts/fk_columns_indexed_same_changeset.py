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
fk_defs = []
for m in re.finditer(r"\balter\s+table\s+([\w\.\"]+)\s+add\s+constraint\s+[\w\"]+\s+foreign\s+key\s*\(([^\)]*)\)", sql_all):
    table = m.group(1)
    cols = [c.strip().strip('"`') for c in m.group(2).split(',') if c.strip()]
    fk_defs.append((table, cols))
indexed_pairs = set()
for m in re.finditer(r"\bcreate\s+(unique\s+)?index\s+[\w\"]+\s+on\s+([\w\.\"]+)\s*\(([^\)]*)\)", sql_all):
    table = m.group(2)
    cols = tuple([c.strip().strip('"`') for c in m.group(3).split(',') if c.strip()])
    indexed_pairs.add((table, cols))
violations = []
for (t, cols) in fk_defs:
    fk_set = set([c.lower() for c in cols])
    ok = False
    for (it, icols) in indexed_pairs:
        if it.lower() == t.lower() and set([c.lower() for c in icols]) == fk_set:
            ok = True
            break
    if not ok:
        violations.append(f"{t}({', '.join(cols)}) has FOREIGN KEY but no matching index in this changeset")
if violations:
    end_fail("Missing indexes for FK columns: " + "; ".join(violations))
else:
    end_ok("All FOREIGN KEY columns appear to have an index created in this changeset.")
