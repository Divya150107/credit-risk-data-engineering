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
# LOAD DTI MAPPING
# ============================================================

cursor.execute(
    """
    SELECT
        credit_profile_key,
        dti
    FROM dim_credit_profile
    """
)

dti_map = {
    credit_profile_key: dti
    for credit_profile_key, dti in cursor.fetchall()
}

print(f"DTI mappings loaded: {len(dti_map):,}")


# ============================================================
# INITIALIZE STATISTICS
# ============================================================

dti_stats = {}


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

        dti = dti_map[credit_profile_key]


        # ----------------------------------------------------
        # Skip missing DTI
        # ----------------------------------------------------

        if dti is None:
            continue


        # ----------------------------------------------------
        # Determine DTI band
        # ----------------------------------------------------

        if dti < 10:
            dti_band = "<10"

        elif dti < 20:
            dti_band = "10-20"

        elif dti < 30:
            dti_band = "20-30"

        elif dti < 40:
            dti_band = "30-40"

        else:
            dti_band = "40+"


        # ----------------------------------------------------
        # Initialize band
        # ----------------------------------------------------

        if dti_band not in dti_stats:

            dti_stats[dti_band] = {
                "total_loans": 0,
                "charged_off_loans": 0
            }


        # ----------------------------------------------------
        # Count loan
        # ----------------------------------------------------

        dti_stats[dti_band]["total_loans"] += 1


        # ----------------------------------------------------
        # Count charge-offs
        # ----------------------------------------------------

        if loan_status == "Charged Off":

            dti_stats[dti_band]["charged_off_loans"] += 1


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
print("Q11 — CHARGE-OFF RATE BY DTI BAND")
print("============================================================")

print(
    f"{'DTI Band':<15}"
    f"{'Total Loans':>15}"
    f"{'Charged Off':>15}"
    f"{'Charge-off %':>15}"
)

print("-" * 60)


band_order = [
    "<10",
    "10-20",
    "20-30",
    "30-40",
    "40+"
]


for band in band_order:

    if band not in dti_stats:
        continue

    total = dti_stats[band]["total_loans"]

    charged_off = dti_stats[band]["charged_off_loans"]

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