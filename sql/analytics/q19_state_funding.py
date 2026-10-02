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
# LOAD GEOGRAPHY MAPPING
# ============================================================

print("\nLoading geography mappings...")

cursor.execute(
    """
    SELECT
        geography_key,
        state_code
    FROM dim_geography
    """
)

state_map = {
    geography_key: state_code
    for geography_key, state_code in cursor.fetchall()
}

print(
    f"State mappings loaded: {len(state_map):,}"
)


# ============================================================
# INITIALIZE STATISTICS
# ============================================================

state_stats = {}


# ============================================================
# PROCESS FACT TABLE IN BATCHES
# ============================================================

print("\nProcessing fact_loan...")

last_key = 0

total_checked = 0


while True:

    # --------------------------------------------------------
    # Fetch next batch
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            loan_fact_key,
            geography_key,
            funded_amount

        FROM fact_loan

        WHERE loan_fact_key > %s

        ORDER BY loan_fact_key

        LIMIT %s
        """,
        (last_key, BATCH_SIZE)
    )

    rows = cursor.fetchall()


    # --------------------------------------------------------
    # Stop when all records are processed
    # --------------------------------------------------------

    if not rows:
        break


    # ========================================================
    # PROCESS CURRENT BATCH
    # ========================================================

    for loan_fact_key, geography_key, funded_amount in rows:

        # ----------------------------------------------------
        # Get state code
        # ----------------------------------------------------

        state_code = state_map[geography_key]


        # ----------------------------------------------------
        # Initialize state
        # ----------------------------------------------------

        if state_code not in state_stats:

            state_stats[state_code] = {
                "loan_count": 0,
                "funded_amount": 0
            }


        # ----------------------------------------------------
        # Count loans
        # ----------------------------------------------------

        state_stats[state_code]["loan_count"] += 1


        # ----------------------------------------------------
        # Add funded amount
        # ----------------------------------------------------

        if funded_amount is not None:

            state_stats[
                state_code
            ]["funded_amount"] += float(
                funded_amount
            )


    # ========================================================
    # UPDATE PROGRESS
    # ========================================================

    total_checked += len(rows)

    last_key = rows[-1][0]

    print(
        f"Processed {total_checked:,} records..."
    )


# ============================================================
# PREPARE RESULTS
# ============================================================

results = []

for state, stats in state_stats.items():

    results.append(
        (
            state,
            stats["loan_count"],
            stats["funded_amount"]
        )
    )


# ------------------------------------------------------------
# Sort by funded amount descending
# ------------------------------------------------------------

results.sort(
    key=lambda x: x[2],
    reverse=True
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n============================================================")
print("Q19 — FUNDED AMOUNT BY STATE")
print("============================================================")

print(
    f"{'State':<10}"
    f"{'Loan Count':>15}"
    f"{'Total Funded Amount':>25}"
)

print("-" * 55)


for state, loan_count, funded_amount in results:

    print(
        f"{state:<10}"
        f"{loan_count:>15,}"
        f"{funded_amount:>25,.2f}"
    )


# ============================================================
# VALIDATION
# ============================================================

total_state_loans = sum(
    stats["loan_count"]
    for stats in state_stats.values()
)

total_state_funding = sum(
    stats["funded_amount"]
    for stats in state_stats.values()
)


print("\n============================================================")
print("Q19 VALIDATION")
print("============================================================")

print(
    f"Records processed       : {total_checked:,}"
)

print(
    f"State loan count        : {total_state_loans:,}"
)

print(
    f"State funded amount     : "
    f"{total_state_funding:,.2f}"
)


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()

connection.close()

print("\nMySQL connection closed.")