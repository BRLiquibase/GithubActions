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
sad_keywords = ["cvv","cvc","cvv2","cav","cav2","pin","pvv","pvki","track1","track_1","track2","track_2","magstripe","mag_stripe","card_validation","service_code"]
violations = []
pattern = re.compile(r"\b(create\s+table|alter\s+table|add\s+column)\b[\s\S]*?;", re.IGNORECASE)
for stmt in pattern.findall(sql_all):
    for kw in sad_keywords:
        if re.search(rf"\b{re.escape(kw)}\b", stmt):
            snippet = stmt.strip().replace("\n"," ")
            if len(snippet)>200: snippet = snippet[:200]+"..."
            violations.append((kw, snippet))
if violations:
    details = "; ".join([f"{kw} in: {snip}" for kw, snip in violations[:5]])
    more = "" if len(violations)<=5 else f" (+{len(violations)-5} more)"
    end_fail(f"PCI DSS: Sensitive authentication data reference detected: {details}{more}")
else:
    end_ok("No obvious PCI sensitive authentication data detected.")
