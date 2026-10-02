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
# LOAD HOME OWNERSHIP MAPPING
# ============================================================

cursor.execute(
    """
    SELECT
        borrower_key,
        home_ownership
    FROM dim_borrower
    """
)

home_map = {
    borrower_key: home_ownership
    for borrower_key, home_ownership in cursor.fetchall()
}

print(
    f"Home ownership mappings loaded: {len(home_map):,}"
)


# ============================================================
# INITIALIZE STATISTICS
# ============================================================

home_stats = {}


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

        home_ownership = home_map[borrower_key]


        if home_ownership is None:
            continue


        # ----------------------------------------------------
        # Initialize category
        # ----------------------------------------------------

        if home_ownership not in home_stats:

            home_stats[home_ownership] = {
                "total_loans": 0,
                "charged_off_loans": 0
            }


        # ----------------------------------------------------
        # Count loans
        # ----------------------------------------------------

        home_stats[
            home_ownership
        ]["total_loans"] += 1


        # ----------------------------------------------------
        # Count charge-offs
        # ----------------------------------------------------

        if loan_status == "Charged Off":

            home_stats[
                home_ownership
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
print("Q13 — CHARGE-OFF RATE BY HOME OWNERSHIP")
print("============================================================")

print(
    f"{'Home Ownership':<20}"
    f"{'Total Loans':>15}"
    f"{'Charged Off':>15}"
    f"{'Charge-off %':>15}"
)

print("-" * 65)


for home_ownership in sorted(home_stats):

    total = home_stats[home_ownership]["total_loans"]

    charged_off = home_stats[home_ownership]["charged_off_loans"]

    charge_off_rate = (
        charged_off / total * 100
    )


    print(
        f"{home_ownership:<20}"
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