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
# LOAD FICO MAPPING
# ============================================================

cursor.execute(
    """
    SELECT
        credit_profile_key,
        fico_score
    FROM dim_credit_profile
    """
)

fico_map = {
    credit_profile_key: fico_score
    for credit_profile_key, fico_score in cursor.fetchall()
}

print(
    f"FICO mappings loaded: {len(fico_map):,}"
)


# ============================================================
# INITIALIZE STATISTICS
# ============================================================

fico_stats = {}


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
            credit_profile_key,
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

    for loan_fact_key, credit_profile_key, loan_status in rows:

        fico_score = fico_map[credit_profile_key]


        # ----------------------------------------------------
        # Determine FICO band
        # ----------------------------------------------------

        if fico_score < 580:
            fico_band = "Poor"

        elif fico_score < 670:
            fico_band = "Fair"

        elif fico_score < 740:
            fico_band = "Good"

        elif fico_score < 800:
            fico_band = "Very Good"

        else:
            fico_band = "Exceptional"


        # ----------------------------------------------------
        # Initialize band
        # ----------------------------------------------------

        if fico_band not in fico_stats:

            fico_stats[fico_band] = {
                "total_loans": 0,
                "charged_off_loans": 0
            }


        # ----------------------------------------------------
        # Count loan
        # ----------------------------------------------------

        fico_stats[fico_band]["total_loans"] += 1


        # ----------------------------------------------------
        # Count charge-offs
        # ----------------------------------------------------

        if loan_status == "Charged Off":

            fico_stats[fico_band]["charged_off_loans"] += 1


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
print("Q10 — CHARGE-OFF RATE BY FICO BAND")
print("============================================================")

print(
    f"{'FICO Band':<15}"
    f"{'Total Loans':>15}"
    f"{'Charged Off':>15}"
    f"{'Charge-off %':>15}"
)

print("-" * 60)


band_order = [
    "Poor",
    "Fair",
    "Good",
    "Very Good",
    "Exceptional"
]


for band in band_order:

    if band not in fico_stats:
        continue

    total = fico_stats[band]["total_loans"]

    charged_off = fico_stats[band]["charged_off_loans"]

    charge_off_rate = (
        charged_off / total * 100
    )


    print(
        f"{band:<15}"
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