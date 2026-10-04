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


# -------------------------------------------------------------
# Database connection
# -------------------------------------------------------------

def get_connection():
    """
    Create and return a MySQL database connection.
    """

    connection = mysql.connector.connect(
        **DB_CONFIG
    )

    print("Connected to MySQL successfully.")

    return connection


# -------------------------------------------------------------
# Loan-level amount reconciliation
# -------------------------------------------------------------

def validate_fact_table():
    """
    Reconcile financial amounts between staging_loan_data
    and fact_loan using set-based SQL validation.

    MySQL performs the comparison across the complete dataset
    instead of transferring millions of records to Python.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------------------------------
        # Step 1: Count staging records
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM staging_loan_data
            """
        )

        records_checked = cursor.fetchone()[0]

        print(
            "\nStarting loan-level amount reconciliation..."
        )

        print(
            f"Records to check : {records_checked:,}"
        )

        # -----------------------------------------------------
        # Step 2: Find financial mismatches
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM staging_loan_data s

            INNER JOIN dim_loan dl
                ON s.id = dl.loan_id

            INNER JOIN fact_loan f
                ON dl.loan_key = f.loan_key

            WHERE

                (
                    s.loan_amnt IS NULL
                    AND f.loan_amount IS NOT NULL
                )
                OR
                (
                    s.loan_amnt IS NOT NULL
                    AND f.loan_amount IS NULL
                )
                OR
                (
                    s.loan_amnt IS NOT NULL
                    AND f.loan_amount IS NOT NULL
                    AND ABS(
                        s.loan_amnt - f.loan_amount
                    ) > 0.01
                )

                OR

                (
                    s.funded_amnt IS NULL
                    AND f.funded_amount IS NOT NULL
                )
                OR
                (
                    s.funded_amnt IS NOT NULL
                    AND f.funded_amount IS NULL
                )
                OR
                (
                    s.funded_amnt IS NOT NULL
                    AND f.funded_amount IS NOT NULL
                    AND ABS(
                        s.funded_amnt - f.funded_amount
                    ) > 0.01
                )

                OR

                (
                    s.funded_amnt_inv IS NULL
                    AND f.funded_amount_investor IS NOT NULL
                )
                OR
                (
                    s.funded_amnt_inv IS NOT NULL
                    AND f.funded_amount_investor IS NULL
                )
                OR
                (
                    s.funded_amnt_inv IS NOT NULL
                    AND f.funded_amount_investor IS NOT NULL
                    AND ABS(
                        s.funded_amnt_inv
                        - f.funded_amount_investor
                    ) > 0.01
                )

                OR

                (
                    s.total_pymnt IS NULL
                    AND f.total_payment IS NOT NULL
                )
                OR
                (
                    s.total_pymnt IS NOT NULL
                    AND f.total_payment IS NULL
                )
                OR
                (
                    s.total_pymnt IS NOT NULL
                    AND f.total_payment IS NOT NULL
                    AND ABS(
                        s.total_pymnt - f.total_payment
                    ) > 0.01
                )

                OR

                (
                    s.total_rec_prncp IS NULL
                    AND f.total_principal_received IS NOT NULL
                )
                OR
                (
                    s.total_rec_prncp IS NOT NULL
                    AND f.total_principal_received IS NULL
                )
                OR
                (
                    s.total_rec_prncp IS NOT NULL
                    AND f.total_principal_received IS NOT NULL
                    AND ABS(
                        s.total_rec_prncp
                        - f.total_principal_received
                    ) > 0.01
                )

                OR

                (
                    s.total_rec_int IS NULL
                    AND f.total_interest_received IS NOT NULL
                )
                OR
                (
                    s.total_rec_int IS NOT NULL
                    AND f.total_interest_received IS NULL
                )
                OR
                (
                    s.total_rec_int IS NOT NULL
                    AND f.total_interest_received IS NOT NULL
                    AND ABS(
                        s.total_rec_int
                        - f.total_interest_received
                    ) > 0.01
                )

                OR

                (
                    s.recoveries IS NULL
                    AND f.recoveries IS NOT NULL
                )
                OR
                (
                    s.recoveries IS NOT NULL
                    AND f.recoveries IS NULL
                )
                OR
                (
                    s.recoveries IS NOT NULL
                    AND f.recoveries IS NOT NULL
                    AND ABS(
                        s.recoveries - f.recoveries
                    ) > 0.01
                )
            """
        )

        mismatches = cursor.fetchone()[0]

        # -----------------------------------------------------
        # Step 3: Check for orphaned records
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM staging_loan_data s

            LEFT JOIN dim_loan dl
                ON s.id = dl.loan_id

            LEFT JOIN fact_loan f
                ON dl.loan_key = f.loan_key

            WHERE dl.loan_key IS NULL
               OR f.loan_key IS NULL
            """
        )

        orphaned_records = cursor.fetchone()[0]

        # -----------------------------------------------------
        # Final result
        # -----------------------------------------------------

        print(
            "\n" + "=" * 60
        )

        print(
            "LOAN-LEVEL RECONCILIATION COMPLETE"
        )

        print(
            "=" * 60
        )

        print(
            f"Records checked : {records_checked:,}"
        )

        print(
            f"Mismatches      : {mismatches:,}"
        )

        print(
            f"Orphaned records: {orphaned_records:,}"
        )

        # -----------------------------------------------------
        # Validation result
        # -----------------------------------------------------

        if mismatches > 0:

            print(
                "\nSTATUS: FAILED"
            )

            raise ValueError(
                "Loan-level financial reconciliation failed."
            )

        if orphaned_records > 0:

            print(
                "\nSTATUS: FAILED"
            )

            raise ValueError(
                "Orphaned staging/fact records detected."
            )

        print(
            "\nSTATUS: PASSED"
        )

        return True

    finally:

        cursor.close()
        connection.close()

        print(
            "\nMySQL connection closed."
        )


# -------------------------------------------------------------
# Standalone execution
# -------------------------------------------------------------

if __name__ == "__main__":

    validate_fact_table()