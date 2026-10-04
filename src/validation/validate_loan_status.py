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

    return mysql.connector.connect(
        **DB_CONFIG
    )


# -------------------------------------------------------------
# Loan status reconciliation
# -------------------------------------------------------------

def validate_loan_status():
    """
    Compare loan-status counts between the staging table
    and the fact table.

    The purpose of this validation is to ensure that the
    warehouse loading process did not lose or alter loan
    status records.
    """

    print("\n" + "=" * 60)
    print("STEP 7: LOAN STATUS RECONCILIATION")
    print("=" * 60)

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------------------------------
        # Get loan-status counts from staging
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT
                loan_status,
                COUNT(*) AS loan_count
            FROM staging_loan_data
            GROUP BY loan_status
            ORDER BY loan_status
            """
        )

        staging_results = cursor.fetchall()

        staging_status = {
            row[0]: row[1]
            for row in staging_results
        }

        # -----------------------------------------------------
        # Get loan-status counts from fact table
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT
                loan_status,
                COUNT(*) AS loan_count
            FROM fact_loan
            GROUP BY loan_status
            ORDER BY loan_status
            """
        )

        fact_results = cursor.fetchall()

        fact_status = {
            row[0]: row[1]
            for row in fact_results
        }

        # -----------------------------------------------------
        # Compare all statuses
        # -----------------------------------------------------

        all_statuses = sorted(
            set(staging_status) |
            set(fact_status)
        )

        mismatches = []

        print(
            f"\n{'Loan Status':<55}"
            f"{'Staging':>15}"
            f"{'Fact':>15}"
        )

        print("-" * 85)

        for status in all_statuses:

            staging_count = staging_status.get(
                status,
                0
            )

            fact_count = fact_status.get(
                status,
                0
            )

            print(
                f"{status:<55}"
                f"{staging_count:>15,}"
                f"{fact_count:>15,}"
            )

            if staging_count != fact_count:

                mismatches.append(
                    {
                        "loan_status": status,
                        "staging_count": staging_count,
                        "fact_count": fact_count
                    }
                )

        # -----------------------------------------------------
        # Final result
        # -----------------------------------------------------

        print("\n" + "-" * 60)

        if mismatches:

            print(
                "✗ STATUS RECONCILIATION FAILED"
            )

            print(
                f"Mismatched statuses: "
                f"{len(mismatches)}"
            )

            for mismatch in mismatches:

                print(
                    f"\nStatus: "
                    f"{mismatch['loan_status']}"
                )

                print(
                    f"Staging: "
                    f"{mismatch['staging_count']:,}"
                )

                print(
                    f"Fact: "
                    f"{mismatch['fact_count']:,}"
                )

            raise ValueError(
                "Loan-status reconciliation failed."
            )

        print(
            "✓ All loan-status counts match."
        )

        print(
            "✓ STATUS RECONCILIATION PASSED"
        )

        return True

    finally:

        cursor.close()
        connection.close()


# -------------------------------------------------------------
# Standalone execution
# -------------------------------------------------------------

if __name__ == "__main__":

    validate_loan_status()