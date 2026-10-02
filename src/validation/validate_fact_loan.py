import mysql.connector
from dotenv import load_dotenv
from pathlib import Path
import os


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

BATCH_SIZE = 25_000


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
# LOAN-LEVEL RECONCILIATION
# ============================================================

print("\nStarting loan-level amount reconciliation...")

last_id = ""
total_checked = 0
total_mismatches = 0


while True:

    # --------------------------------------------------------
    # Get one batch
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            s.id,
            s.loan_amnt,
            f.loan_amount

        FROM staging_loan_data s

        JOIN dim_loan d
            ON s.id = d.loan_id

        JOIN fact_loan f
            ON d.loan_key = f.loan_key

        WHERE s.id > %s

        ORDER BY s.id

        LIMIT %s
        """,
        (last_id, BATCH_SIZE)
    )

    rows = cursor.fetchall()


    # --------------------------------------------------------
    # Stop when all records are processed
    # --------------------------------------------------------

    if not rows:
        break


    # --------------------------------------------------------
    # Compare loan amounts
    # --------------------------------------------------------

    for loan_id, staging_amount, warehouse_amount in rows:

        if staging_amount is None and warehouse_amount is None:
            continue

        if staging_amount is None or warehouse_amount is None:

            total_mismatches += 1

            print(
                f"Mismatch: {loan_id} | "
                f"Staging={staging_amount} | "
                f"Warehouse={warehouse_amount}"
            )

        elif abs(float(staging_amount) - float(warehouse_amount)) > 0.01:

            total_mismatches += 1

            print(
                f"Mismatch: {loan_id} | "
                f"Staging={staging_amount} | "
                f"Warehouse={warehouse_amount}"
            )


    # --------------------------------------------------------
    # Update progress
    # --------------------------------------------------------

    total_checked += len(rows)

    last_id = rows[-1][0]

    print(
        f"Checked {total_checked:,} records..."
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n============================================================")
print("LOAN-LEVEL RECONCILIATION COMPLETE")
print("============================================================")

print(f"Records checked : {total_checked:,}")
print(f"Mismatches      : {total_mismatches:,}")


if total_mismatches == 0:

    print("\nSTATUS: PASSED")

else:

    print("\nSTATUS: FAILED")


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nMySQL connection closed.")