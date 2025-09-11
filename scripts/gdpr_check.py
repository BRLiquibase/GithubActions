# import Liquibase modules containing useful functions
import liquibase_utilities as lb
import sys

# define reusable variables
obj = lb.get_database_object()  # database or changelog object to examine
liquibase_status = lb.get_status()  # Status object of the check

# -----------------------------
# GDPR keyword catalog (names only; no regex/imports)
# -----------------------------
_GDPR_TOKENS = [
    # Names
    "name", "full_name", "firstname", "first_name", "givenname", "given_name",
    "lastname", "last_name", "surname", "middlename", "middle_name", "maiden_name",
    # Contact
    "email", "emailaddress", "email_address", "phone", "telephone", "mobile",
    "cell", "msisdn",
    # Address / location
    "address", "address1", "address2", "street", "street1", "street2",
    "city", "town", "county", "state", "province", "region",
    "postal", "postcode", "postalcode", "zip", "zipcode", "country",
    "latitude", "longitude", "lat", "lon", "geocode",
    # DOB / age
    "dob", "dateofbirth", "date_of_birth", "birthdate", "birthday", "age", "yob",
    # Government IDs / identifiers
    "ssn", "sin", "nin", "nino", "nationalinsurance", "national_insurance",
    "nationalid", "national_id", "passport", "passportno", "passport_number",
    "driverslicense", "driver_license", "driving_license", "license_number",
    "taxid", "tax_id", "tin", "ein", "itn",
    "siret", "siren", "nif", "nie", "curp", "rfc",
    "aadhaar", "pan", "uin", "bsn", "pesel",
    # Financial
    "iban", "bic", "swift", "bankaccount", "bank_account", "accountno",
    "account_number", "cardnumber", "card_number", "creditcard", "ccnum",
    "cc_number", "cvv", "cvc", "expiry", "exp_date",
    # Online identifiers
    "ip", "ipaddress", "ip_address", "ipv4", "ipv6", "mac",
    "deviceid", "device_id", "cookie", "session", "sessionid", "session_id",
    "trackingid", "tracking_id", "useragent", "user_agent", "userid", "user_id", "username",
    # Health (special category)
    "nhs_number", "medical", "health", "diagnosis", "patientid", "patient_id", "patient",
    # Biometric (special category)
    "biometric", "fingerprint", "face", "iris", "retina", "voiceprint", "dna"
]

# Normalize and match helpers (no regex)
def _normalize(s):
    s = (s or "").lower()
    out = []
    for ch in s:
        # keep only letters and digits; everything else becomes nothing
        if ch.isalnum():
            out.append(ch)
    return "".join(out)

def _matches_gdpr(name):
    n = _normalize(name)
    for token in _GDPR_TOKENS:
        if token in n:
            return token
    return None

def _safe_get_name(x):
    try:
        return x.getName()
    except Exception:
        try:
            return str(x)
        except Exception:
            return None

def _collect_table_columns(table_obj):
    # Try typical column access patterns without importing anything else
    cols = []
    try:
        got = table_obj.getColumns()
        if got:
            cols = list(got)
    except Exception:
        try:
            got = lb.get_columns(table_obj)
            if got:
                cols = list(got)
        except Exception:
            cols = []
    return cols

# -----------------------------
# Check logic
# -----------------------------

# If the current object is a TABLE, scan its columns
if lb.is_table(obj):
    table_name = _safe_get_name(obj)
    offending = []
    for col in _collect_table_columns(obj):
        col_name = _safe_get_name(col)
        if col_name:
            token = _matches_gdpr(col_name)
            if token:
                offending.append(col_name)
    if offending:
        liquibase_status.fired = True
        liquibase_status.message = (
            "GDPR: Table '{tbl}' contains potential personal-data columns: {cols}. "
            "Review retention, masking, and access controls."
        ).format(tbl=table_name, cols=", ".join(sorted(set(offending))))
        sys.exit(1)

# If the current object is a COLUMN, check its name directly
# (Works when Liquibase iterates columns as individual objects.)
try:
    if lb.is_column(obj):
        col_name = _safe_get_name(obj)
        token = _matches_gdpr(col_name)
        if token:
            # Try to include parent table if available
            table_name = None
            try:
                parent = obj.getTable()
                table_name = _safe_get_name(parent)
            except Exception:
                table_name = None
            if table_name:
                msg = "GDPR: Column '{col}' in table '{tbl}' may contain personal data."
                msg = msg.format(col=col_name, tbl=table_name)
            else:
                msg = "GDPR: Column '{col}' may contain personal data.".format(col=col_name)
            liquibase_status.fired = True
            liquibase_status.message = msg + " Review retention, masking, and access controls."
            sys.exit(1)
except Exception:
    # If the environment doesn't provide lb.is_column or obj isn't a column-like object, ignore.
    pass

# default return code
False
