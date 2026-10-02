import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import os


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "lending_club_cleaned.csv"
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# MYSQL CONNECTION
# ============================================================

connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
    allow_local_infile=True
)

cursor = connection.cursor()

print("Connected to MySQL.")


# ============================================================
# LOAD CSV INTO STAGING TABLE
# ============================================================

print("Loading cleaned dataset into MySQL...")
print(f"File: {CSV_PATH}")

load_query = f"""
LOAD DATA LOCAL INFILE '{CSV_PATH.as_posix()}'
INTO TABLE staging_loan_data
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(
    id,
    loan_amnt,
    funded_amnt,
    funded_amnt_inv,
    term,
    int_rate,
    installment,
    grade,
    sub_grade,
    emp_title,
    emp_length,
    home_ownership,
    annual_inc,
    verification_status,
    addr_state,
    dti,
    delinq_2yrs,
    fico_range_low,
    fico_range_high,
    inq_last_6mths,
    open_acc,
    pub_rec,
    revol_bal,
    revol_util,
    total_acc,
    issue_d,
    loan_status,
    purpose,
    application_type,
    initial_list_status,
    out_prncp,
    total_pymnt,
    total_rec_prncp,
    total_rec_int,
    total_rec_late_fee,
    recoveries,
    collection_recovery_fee,
    last_pymnt_d,
    last_pymnt_amnt,
    fico_score
)
"""

cursor.execute(load_query)

connection.commit()

print("Data loaded successfully.")


# ============================================================
# VERIFY ROW COUNT
# ============================================================

cursor.execute(
    "SELECT COUNT(*) FROM staging_loan_data"
)

row_count = cursor.fetchone()[0]

print(f"\nRows in staging table: {row_count:,}")


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nMySQL loading complete.")