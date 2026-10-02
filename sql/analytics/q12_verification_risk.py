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
# LOAD VERIFICATION STATUS MAPPING
# ============================================================

cursor.execute(
    """
    SELECT
        borrower_key,
        verification_status
    FROM dim_borrower
    """
)

verification_map = {
    borrower_key: verification_status
    for borrower_key, verification_status in cursor.fetchall()
}

print(
    f"Verification mappings loaded: {len(verification_map):,}"
)


# ============================================================
# INITIALIZE STATISTICS
# ============================================================

verification_stats = {}


# ============================================================
# PROCESS FACT TABLE IN BATCHES
# ============================================================

print("\nProcessing fact_loan...")

last_key = 0
total_checked = 0


while True:

    cursor.execute(
        """
        SELECT
            loan_fact_key,
            borrower_key,
            loan_status

        FROM fact_loan

        WHERE loan_fact_key > %s

        ORDER BY loan_fact_key

        LIMIT %s
        """,
        (last_key, BATCH_SIZE)
    )

    rows = cursor.fetchall()

    if not rows:
        break


    # --------------------------------------------------------
    # Process current batch
    # --------------------------------------------------------

    for loan_fact_key, borrower_key, loan_status in rows:

        verification_status = verification_map[borrower_key]


        if verification_status is None:
            continue


        # ----------------------------------------------------
        # Initialize category
        # ----------------------------------------------------

        if verification_status not in verification_stats:

            verification_stats[verification_status] = {
                "total_loans": 0,
                "charged_off_loans": 0
            }


        # ----------------------------------------------------
        # Count loan
        # ----------------------------------------------------

        verification_stats[verification_status]["total_loans"] += 1


        # ----------------------------------------------------
        # Count charge-offs
        # ----------------------------------------------------

        if loan_status == "Charged Off":

            verification_stats[
                verification_status
            ]["charged_off_loans"] += 1


    # --------------------------------------------------------
    # Update progress
    # --------------------------------------------------------

    total_checked += len(rows)

    last_key = rows[-1][0]

    print(
        f"Processed {total_checked:,} records..."
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n============================================================")
print("Q12 — CHARGE-OFF RATE BY VERIFICATION STATUS")
print("============================================================")

print(
    f"{'Verification Status':<25}"
    f"{'Total Loans':>15}"
    f"{'Charged Off':>15}"
    f"{'Charge-off %':>15}"
)

print("-" * 70)


for status in sorted(verification_stats):

    total = verification_stats[status]["total_loans"]

    charged_off = verification_stats[status]["charged_off_loans"]

    charge_off_rate = (
        charged_off / total * 100
    )


    print(
        f"{status:<25}"
        f"{total:>15,}"
        f"{charged_off:>15,}"
        f"{charge_off_rate:>14.2f}%"
    )


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nMySQL connection closed.")