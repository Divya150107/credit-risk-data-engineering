import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


# -------------------------------------------------------------
# Project configuration
# -------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}


BATCH_SIZE = 25_000


# -------------------------------------------------------------
# Database connection
# -------------------------------------------------------------

def get_connection():
    """
    Create and return a MySQL database connection.
    """

    return mysql.connector.connect(**DB_CONFIG)


# -------------------------------------------------------------
# Load dim_loan
# -------------------------------------------------------------

def load_dim_loan(connection):
    """
    Load the loan dimension from staging_loan_data.
    """

    print("\nLoading dim_loan...")

    cursor = connection.cursor()

    last_id = ""
    total_loaded = 0

    try:

        while True:

            cursor.execute(
                """
                SELECT
                    id,
                    term,
                    grade,
                    sub_grade,
                    purpose,
                    application_type,
                    initial_list_status
                FROM staging_loan_data
                WHERE id > %s
                ORDER BY id
                LIMIT %s
                """,
                (last_id, BATCH_SIZE)
            )

            rows = cursor.fetchall()

            if not rows:
                break

            cursor.executemany(
                """
                INSERT INTO dim_loan (
                    loan_id,
                    loan_term_months,
                    grade,
                    sub_grade,
                    purpose,
                    application_type,
                    initial_list_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                rows
            )

            connection.commit()

            total_loaded += len(rows)
            last_id = rows[-1][0]

            print(
                f"dim_loan loaded: "
                f"{total_loaded:,}"
            )

        print(
            f"✓ dim_loan completed: "
            f"{total_loaded:,} rows"
        )

        return total_loaded

    finally:
        cursor.close()


# -------------------------------------------------------------
# Load dim_borrower
# -------------------------------------------------------------

def load_dim_borrower(connection):
    """
    Load the borrower dimension from staging_loan_data.
    """

    print("\nLoading dim_borrower...")

    cursor = connection.cursor()

    last_id = ""
    total_loaded = 0

    try:

        while True:

            cursor.execute(
                """
                SELECT
                    id,
                    emp_title,
                    emp_length,
                    home_ownership,
                    annual_inc,
                    verification_status
                FROM staging_loan_data
                WHERE id > %s
                ORDER BY id
                LIMIT %s
                """,
                (last_id, BATCH_SIZE)
            )

            rows = cursor.fetchall()

            if not rows:
                break

            cursor.executemany(
                """
                INSERT INTO dim_borrower (
                    loan_id,
                    emp_title,
                    emp_length_years,
                    home_ownership,
                    annual_income,
                    verification_status
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                rows
            )

            connection.commit()

            total_loaded += len(rows)
            last_id = rows[-1][0]

            print(
                f"dim_borrower loaded: "
                f"{total_loaded:,}"
            )

        print(
            f"✓ dim_borrower completed: "
            f"{total_loaded:,} rows"
        )

        return total_loaded

    finally:
        cursor.close()


# -------------------------------------------------------------
# Load dim_credit_profile
# -------------------------------------------------------------

def load_dim_credit_profile(connection):
    """
    Load the credit-profile dimension from staging_loan_data.
    """

    print("\nLoading dim_credit_profile...")

    cursor = connection.cursor()

    last_id = ""
    total_loaded = 0

    try:

        while True:

            cursor.execute(
                """
                SELECT
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
                FROM staging_loan_data
                WHERE id > %s
                ORDER BY id
                LIMIT %s
                """,
                (last_id, BATCH_SIZE)
            )

            rows = cursor.fetchall()

            if not rows:
                break

            cursor.executemany(
                """
                INSERT INTO dim_credit_profile (
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
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows
            )

            connection.commit()

            total_loaded += len(rows)
            last_id = rows[-1][0]

            print(
                f"dim_credit_profile loaded: "
                f"{total_loaded:,}"
            )

        print(
            f"✓ dim_credit_profile completed: "
            f"{total_loaded:,} rows"
        )

        return total_loaded

    finally:
        cursor.close()


# -------------------------------------------------------------
# Main dimension-loading function
# -------------------------------------------------------------

def load_dimensions():

    print("\n" + "=" * 60)
    print("STEP 4: LOAD LARGE DIMENSIONS")
    print("=" * 60)

    connection = get_connection()

    try:

        # Start with empty dimension tables.
        #
        # This makes the pipeline rerunnable.
        # Foreign keys are temporarily disabled because
        # fact_loan references these dimensions.

        cursor = connection.cursor()

        cursor.execute(
            "SET FOREIGN_KEY_CHECKS = 0"
        )

        cursor.execute(
            "TRUNCATE TABLE dim_loan"
        )

        cursor.execute(
            "TRUNCATE TABLE dim_borrower"
        )

        cursor.execute(
            "TRUNCATE TABLE dim_credit_profile"
        )

        cursor.execute(
            "SET FOREIGN_KEY_CHECKS = 1"
        )

        connection.commit()

        cursor.close()

        # Load dimensions

        loan_count = load_dim_loan(connection)

        borrower_count = load_dim_borrower(connection)

        credit_count = load_dim_credit_profile(connection)

        print("\n" + "-" * 60)

        print(
            f"dim_loan:           {loan_count:,}"
        )

        print(
            f"dim_borrower:       {borrower_count:,}"
        )

        print(
            f"dim_credit_profile: {credit_count:,}"
        )

        print("\n✓ Large dimensions loaded successfully.")

        return {
            "dim_loan": loan_count,
            "dim_borrower": borrower_count,
            "dim_credit_profile": credit_count
        }

    except Exception:

        connection.rollback()

        print(
            "\n✗ Dimension loading failed."
        )

        raise

    finally:

        connection.close()


# -------------------------------------------------------------
# Standalone execution
# -------------------------------------------------------------

if __name__ == "__main__":

    load_dimensions()