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
# LOAD DATE MAPPING
# ============================================================

cursor.execute(
    """
    SELECT
        date_key,
        year
    FROM dim_date
    """
)

year_map = {
    date_key: year
    for date_key, year in cursor.fetchall()
}

print(f"Date mappings loaded: {len(year_map):,}")


# ============================================================
# INITIALIZE YEARLY STATISTICS
# ============================================================

year_stats = {}


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
            issue_date_key,
            loan_status,
            loan_amount,
            funded_amount

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

    for (
        loan_fact_key,
        issue_date_key,
        loan_status,
        loan_amount,
        funded_amount
    ) in rows:

        year = year_map[issue_date_key]


        # ----------------------------------------------------
        # Initialize year
        # ----------------------------------------------------

        if year not in year_stats:

            year_stats[year] = {
                "loan_count": 0,
                "loan_amount": 0,
                "funded_amount": 0,
                "charged_off_loans": 0
            }


        # ----------------------------------------------------
        # Loan count
        # ----------------------------------------------------

        year_stats[year]["loan_count"] += 1


        # ----------------------------------------------------
        # Loan amount
        # ----------------------------------------------------

        if loan_amount is not None:

            year_stats[year]["loan_amount"] += float(
                loan_amount
            )


        # ----------------------------------------------------
        # Funded amount
        # ----------------------------------------------------

        if funded_amount is not None:

            year_stats[year]["funded_amount"] += float(
                funded_amount
            )


        # ----------------------------------------------------
        # Charged-off loans
        # ----------------------------------------------------

        if loan_status == "Charged Off":

            year_stats[year]["charged_off_loans"] += 1


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
print("Q20 — LOAN ORIGINATION AND CHARGE-OFF RATE BY YEAR")
print("============================================================")

print(
    f"{'Year':<10}"
    f"{'Loan Count':>15}"
    f"{'Loan Amount':>20}"
    f"{'Funded Amount':>20}"
    f"{'Charged Off':>15}"
    f"{'Charge-off %':>15}"
)

print("-" * 95)


# Sort chronologically

for year in sorted(year_stats):

    stats = year_stats[year]

    total_loans = stats["loan_count"]

    charged_off = stats["charged_off_loans"]

    charge_off_rate = (
        charged_off / total_loans * 100
    )


    print(
        f"{year:<10}"
        f"{total_loans:>15,}"
        f"{stats['loan_amount']:>20,.2f}"
        f"{stats['funded_amount']:>20,.2f}"
        f"{charged_off:>15,}"
        f"{charge_off_rate:>14.2f}%"
    )


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nMySQL connection closed.")