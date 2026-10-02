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
# LOAD LOAN -> GRADE MAPPING
# ============================================================

cursor.execute(
    """
    SELECT loan_key, grade
    FROM dim_loan
    """
)

grade_map = {
    loan_key: grade
    for loan_key, grade in cursor.fetchall()
}

print(f"Grade mappings loaded: {len(grade_map):,}")


# ============================================================
# INITIALIZE COUNTERS
# ============================================================

grade_stats = {}


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
    # Aggregate current batch
    # --------------------------------------------------------

    for loan_fact_key, loan_key, loan_status in rows:

        grade = grade_map[loan_key]

        if grade not in grade_stats:

            grade_stats[grade] = {
                "total_loans": 0,
                "charged_off_loans": 0
            }


        grade_stats[grade]["total_loans"] += 1


        if loan_status == "Charged Off":

            grade_stats[grade]["charged_off_loans"] += 1


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
print("Q8 — CHARGE-OFF RATE BY LOAN GRADE")
print("============================================================")

print(
    f"{'Grade':<10}"
    f"{'Total Loans':>15}"
    f"{'Charged Off':>15}"
    f"{'Charge-off %':>15}"
)

print("-" * 55)


for grade in sorted(grade_stats):

    total = grade_stats[grade]["total_loans"]

    charged_off = grade_stats[grade]["charged_off_loans"]

    charge_off_rate = (
        charged_off / total * 100
    )


    print(
        f"{grade:<10}"
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