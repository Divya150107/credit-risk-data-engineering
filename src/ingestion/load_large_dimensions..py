import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import os


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# MYSQL CONNECTION
# ============================================================

connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
)

cursor = connection.cursor()

print("Connected to MySQL.")


# ============================================================
# SETTINGS
# ============================================================

BATCH_SIZE = 25_000


# ============================================================
# FUNCTION: LOAD DIMENSION IN BATCHES
# ============================================================

def load_dimension(
    dimension_name,
    select_columns,
    insert_columns
):

    print("\n" + "=" * 60)
    print(f"Loading {dimension_name}")
    print("=" * 60)

    last_id = ""

    total_loaded = 0

    while True:

        # ----------------------------------------------------
        # Fetch next batch from staging
        # ----------------------------------------------------

        select_query = f"""
            SELECT
                {select_columns}
            FROM staging_loan_data
            WHERE id > %s
            ORDER BY id
            LIMIT %s
        """

        cursor.execute(
            select_query,
            (last_id, BATCH_SIZE)
        )

        rows = cursor.fetchall()

        if not rows:
            break

        # ----------------------------------------------------
        # Insert batch into dimension
        # ----------------------------------------------------

        placeholders = ", ".join(
            ["%s"] * len(insert_columns.split(","))
        )

        insert_query = f"""
            INSERT INTO {dimension_name}
            ({insert_columns})
            VALUES ({placeholders})
        """

        cursor.executemany(
            insert_query,
            rows
        )

        connection.commit()

        # ----------------------------------------------------
        # Update progress
        # ----------------------------------------------------

        last_id = rows[-1][0]

        total_loaded += len(rows)

        print(
            f"{dimension_name}: "
            f"{total_loaded:,} rows loaded"
        )

    print(
        f"{dimension_name} complete: "
        f"{total_loaded:,} rows"
    )


# ============================================================
# 1. DIM LOAN
# ============================================================

load_dimension(
    dimension_name="dim_loan",

    select_columns="""
        id,
        term,
        grade,
        sub_grade,
        purpose,
        application_type,
        initial_list_status
    """,

    insert_columns="""
        loan_id,
        loan_term_months,
        grade,
        sub_grade,
        purpose,
        application_type,
        initial_list_status
    """
)


# ============================================================
# 2. DIM BORROWER
# ============================================================

load_dimension(
    dimension_name="dim_borrower",

    select_columns="""
        id,
        emp_title,
        emp_length,
        home_ownership,
        annual_inc,
        verification_status
    """,

    insert_columns="""
        loan_id,
        emp_title,
        emp_length_years,
        home_ownership,
        annual_income,
        verification_status
    """
)


# ============================================================
# 3. DIM CREDIT PROFILE
# ============================================================

load_dimension(
    dimension_name="dim_credit_profile",

    select_columns="""
        id,
        fico_score,
        dti,
        delinq_2yrs,
        inq_last_6mths,
        open_acc,
        pub_rec,
        revol_bal,
        revol_util,
        total_acc
    """,

    insert_columns="""
        loan_id,
        fico_score,
        dti,
        delinq_2yrs,
        inq_last_6mths,
        open_acc,
        pub_rec,
        revol_bal,
        revol_util,
        total_acc
    """
)


# ============================================================
# VERIFY COUNTS
# ============================================================

print("\n" + "=" * 60)
print("WAREHOUSE DIMENSION COUNTS")
print("=" * 60)

tables = [
    "dim_loan",
    "dim_borrower",
    "dim_credit_profile"
]

for table in tables:

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cursor.fetchone()[0]

    print(f"{table:<25}: {count:,}")


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nLarge dimension loading complete.")