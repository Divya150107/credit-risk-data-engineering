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
# LOAD GRADE MAPPING
# ============================================================

cursor.execute(
    """
    SELECT
        loan_key,
        grade
    FROM dim_loan
    """
)

grade_map = {
    loan_key: grade
    for loan_key, grade in cursor.fetchall()
}

print(f"Grade mappings loaded: {len(grade_map):,}")


# ============================================================
# INITIALIZE STATISTICS
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
            outstanding_principal

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

    for loan_fact_key, loan_key, outstanding_principal in rows:

        grade = grade_map[loan_key]


        if grade not in grade_stats:

            grade_stats[grade] = {
                "loan_count": 0,
                "outstanding_principal": 0
            }


        grade_stats[grade]["loan_count"] += 1


        if outstanding_principal is not None:

            grade_stats[
                grade
            ]["outstanding_principal"] += float(
                outstanding_principal
            )


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
print("Q18 — OUTSTANDING PRINCIPAL BY LOAN GRADE")
print("============================================================")

print(
    f"{'Grade':<10}"
    f"{'Loan Count':>15}"
    f"{'Outstanding Principal':>25}"
)

print("-" * 55)


# Sort by outstanding principal descending

results = []

for grade, stats in grade_stats.items():

    results.append(
        (
            grade,
            stats["loan_count"],
            stats["outstanding_principal"]
        )
    )


results.sort(
    key=lambda x: x[2],
    reverse=True
)


for grade, loan_count, outstanding_principal in results:

    print(
        f"{grade:<10}"
        f"{loan_count:>15,}"
        f"{outstanding_principal:>25,.2f}"
    )


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nMySQL connection closed.")