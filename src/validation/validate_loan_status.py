import mysql.connector
from dotenv import load_dotenv
from pathlib import Path
import os


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

cursor = connection.cursor()

print("Connected to MySQL successfully.")


# ============================================================
# GET STATUS COUNTS FROM STAGING
# ============================================================

print("\nReading loan status counts from staging...")

cursor.execute(
    """
    SELECT
        loan_status,
        COUNT(*) AS record_count
    FROM staging_loan_data
    GROUP BY loan_status
    """
)

staging_counts = {
    status: count
    for status, count in cursor.fetchall()
}


# ============================================================
# GET STATUS COUNTS FROM FACT TABLE
# ============================================================

print("Reading loan status counts from fact table...")

cursor.execute(
    """
    SELECT
        loan_status,
        COUNT(*) AS record_count
    FROM fact_loan
    GROUP BY loan_status
    """
)

warehouse_counts = {
    status: count
    for status, count in cursor.fetchall()
}


# ============================================================
# COMPARE RESULTS
# ============================================================

print("\n============================================================")
print("LOAN STATUS RECONCILIATION")
print("============================================================")

all_statuses = set(staging_counts) | set(warehouse_counts)

total_mismatches = 0

for status in sorted(all_statuses):

    staging_count = staging_counts.get(status, 0)

    warehouse_count = warehouse_counts.get(status, 0)

    difference = staging_count - warehouse_count

    print(
        f"{str(status):55} "
        f"Staging: {staging_count:10,} | "
        f"Warehouse: {warehouse_count:10,} | "
        f"Difference: {difference:8,}"
    )

    if difference != 0:
        total_mismatches += 1


# ============================================================
# FINAL RESULT
# ============================================================

print("\n============================================================")
print("STATUS RECONCILIATION COMPLETE")
print("============================================================")

print(f"Status mismatches : {total_mismatches}")


if total_mismatches == 0:
    print("STATUS: PASSED")
else:
    print("STATUS: FAILED")


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nMySQL connection closed.")