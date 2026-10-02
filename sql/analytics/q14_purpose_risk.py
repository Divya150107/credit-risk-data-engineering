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
# LOAD PURPOSE MAPPING
# ============================================================

cursor.execute(
    """
    SELECT
        loan_key,
        purpose
    FROM dim_loan
    """
)

purpose_map = {
    loan_key: purpose
    for loan_key, purpose in cursor.fetchall()
}

print(f"Purpose mappings loaded: {len(purpose_map):,}")


# ============================================================
# INITIALIZE STATISTICS
# ============================================================

purpose_stats = {}


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
            loan_key,
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

    for loan_fact_key, loan_key, loan_status in rows:

        purpose = purpose_map[loan_key]


        if purpose is None:
            continue


        # ----------------------------------------------------
        # Initialize purpose
        # ----------------------------------------------------

        if purpose not in purpose_stats:

            purpose_stats[purpose] = {
                "total_loans": 0,
                "charged_off_loans": 0
            }


        # ----------------------------------------------------
        # Count loans
        # ----------------------------------------------------

        purpose_stats[purpose]["total_loans"] += 1


        # ----------------------------------------------------
        # Count charge-offs
        # ----------------------------------------------------

        if loan_status == "Charged Off":

            purpose_stats[purpose]["charged_off_loans"] += 1


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
print("Q14 — CHARGE-OFF RATE BY LOAN PURPOSE")
print("============================================================")

print(
    f"{'Purpose':<25}"
    f"{'Total Loans':>15}"
    f"{'Charged Off':>15}"
    f"{'Charge-off %':>15}"
)

print("-" * 70)


# Only display purposes with at least 100 loans

results = []

for purpose, stats in purpose_stats.items():

    total = stats["total_loans"]

    charged_off = stats["charged_off_loans"]

    if total < 100:
        continue

    charge_off_rate = (
        charged_off / total * 100
    )

    results.append(
        (
            purpose,
            total,
            charged_off,
            charge_off_rate
        )
    )


# Sort by charge-off rate

results.sort(
    key=lambda x: x[3],
    reverse=True
)


for purpose, total, charged_off, charge_off_rate in results:

    print(
        f"{purpose:<25}"
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