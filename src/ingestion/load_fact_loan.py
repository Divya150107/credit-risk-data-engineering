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
# Load fact_loan
# -------------------------------------------------------------

def load_fact_table():

    print("\n" + "=" * 60)
    print("STEP 5: LOAD FACT TABLE")
    print("=" * 60)

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------------------------------
        # Clear existing fact data
        # -----------------------------------------------------

        print("\nClearing existing fact_loan data...")

        cursor.execute(
            "TRUNCATE TABLE fact_loan"
        )

        connection.commit()

        # -----------------------------------------------------
        # Load fact table in batches
        # -----------------------------------------------------

        print("\nLoading fact_loan...")

        last_id = ""
        total_loaded = 0

        while True:

            cursor.execute(
                """
                SELECT
                    s.id,
                    s.issue_d,
                    s.loan_status,
                    s.loan_amnt,
                    s.funded_amnt,
                    s.funded_amnt_inv,
                    s.int_rate,
                    s.installment,
                    s.out_prncp,
                    s.total_pymnt,
                    s.total_rec_prncp,
                    s.total_rec_int,
                    s.total_rec_late_fee,
                    s.recoveries,
                    s.collection_recovery_fee,
                    s.last_pymnt_d,
                    s.last_pymnt_amnt
                FROM staging_loan_data s
                WHERE s.id > %s
                ORDER BY s.id
                LIMIT %s
                """,
                (last_id, BATCH_SIZE)
            )

            rows = cursor.fetchall()

            if not rows:
                break

            # -------------------------------------------------
            # Insert each batch
            # -------------------------------------------------

            insert_rows = []

            for row in rows:

                (
                    loan_id,
                    issue_date,
                    loan_status,
                    loan_amount,
                    funded_amount,
                    funded_amount_investor,
                    interest_rate,
                    installment,
                    outstanding_principal,
                    total_payment,
                    total_principal_received,
                    total_interest_received,
                    total_late_fees,
                    recoveries,
                    collection_recovery_fee,
                    last_payment_date,
                    last_payment_amount
                ) = row

                # ---------------------------------------------
                # Retrieve surrogate keys
                # ---------------------------------------------

                cursor.execute(
                    """
                    SELECT loan_key
                    FROM dim_loan
                    WHERE loan_id = %s
                    """,
                    (loan_id,)
                )

                loan_key = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT borrower_key
                    FROM dim_borrower
                    WHERE loan_id = %s
                    """,
                    (loan_id,)
                )

                borrower_key = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT credit_profile_key
                    FROM dim_credit_profile
                    WHERE loan_id = %s
                    """,
                    (loan_id,)
                )

                credit_profile_key = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT geography_key
                    FROM dim_geography g
                    JOIN staging_loan_data s
                        ON g.state_code = s.addr_state
                    WHERE s.id = %s
                    """,
                    (loan_id,)
                )

                geography_key = cursor.fetchone()[0]

                # ---------------------------------------------
                # Retrieve date key
                # ---------------------------------------------

                if issue_date is not None:

                    cursor.execute(
                        """
                        SELECT date_key
                        FROM dim_date
                        WHERE full_date = %s
                        """,
                        (issue_date,)
                    )

                    date_result = cursor.fetchone()

                    issue_date_key = (
                        date_result[0]
                        if date_result
                        else None
                    )

                else:
                    issue_date_key = None

                # ---------------------------------------------
                # Prepare fact record
                # ---------------------------------------------

                insert_rows.append(
                    (
                        loan_key,
                        borrower_key,
                        credit_profile_key,
                        geography_key,
                        issue_date_key,
                        loan_status,
                        loan_amount,
                        funded_amount,
                        funded_amount_investor,
                        interest_rate,
                        installment,
                        outstanding_principal,
                        total_payment,
                        total_principal_received,
                        total_interest_received,
                        total_late_fees,
                        recoveries,
                        collection_recovery_fee,
                        last_payment_date,
                        last_payment_amount
                    )
                )

            # -------------------------------------------------
            # Insert batch
            # -------------------------------------------------

            cursor.executemany(
                """
                INSERT INTO fact_loan (
                    loan_key,
                    borrower_key,
                    credit_profile_key,
                    geography_key,
                    issue_date_key,
                    loan_status,
                    loan_amount,
                    funded_amount,
                    funded_amount_investor,
                    interest_rate,
                    installment,
                    outstanding_principal,
                    total_payment,
                    total_principal_received,
                    total_interest_received,
                    total_late_fees,
                    recoveries,
                    collection_recovery_fee,
                    last_payment_date,
                    last_payment_amount
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                """,
                insert_rows
            )

            connection.commit()

            total_loaded += len(rows)

            last_id = rows[-1][0]

            print(
                f"fact_loan loaded: "
                f"{total_loaded:,}"
            )

        # -----------------------------------------------------
        # Final count
        # -----------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM fact_loan"
        )

        fact_count = cursor.fetchone()[0]

        print(
            f"\nFinal fact_loan count: "
            f"{fact_count:,}"
        )

        if fact_count == 0:

            raise RuntimeError(
                "fact_loan loading completed but "
                "the table contains zero rows."
            )

        print(
            "\n✓ fact_loan loaded successfully."
        )

        return fact_count

    except Exception:

        connection.rollback()

        print(
            "\n✗ Fact table loading failed."
        )

        raise

    finally:

        cursor.close()
        connection.close()


# -------------------------------------------------------------
# Standalone execution
# -------------------------------------------------------------

if __name__ == "__main__":

    load_fact_table()