import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


# -------------------------------------------------------------
# Project paths
# -------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "lending_club_cleaned.csv"
)


# -------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")


# -------------------------------------------------------------
# Database configuration
# -------------------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "allow_local_infile": True
}


def get_connection():
    """
    Create and return a MySQL database connection.
    """

    return mysql.connector.connect(**DB_CONFIG)


def load_to_staging():
    """
    Load the cleaned CSV into the MySQL staging table.
    """

    print("\n" + "=" * 60)
    print("STEP 3: LOAD DATA INTO STAGING")
    print("=" * 60)

    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed file not found:\n{PROCESSED_DATA_PATH}"
        )

    print(f"Loading file:\n{PROCESSED_DATA_PATH}")

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------------------------------
        # Clear existing staging data
        # -----------------------------------------------------

        print("\nClearing existing staging data...")

        cursor.execute(
            "TRUNCATE TABLE staging_loan_data"
        )

        # -----------------------------------------------------
        # Load CSV into staging table
        # -----------------------------------------------------

        load_sql = f"""
        LOAD DATA LOCAL INFILE '{PROCESSED_DATA_PATH.as_posix()}'
        INTO TABLE staging_loan_data
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        IGNORE 1 ROWS
        (
            id,
            loan_amnt,
            funded_amnt,
            funded_amnt_inv,
            term,
            int_rate,
            installment,
            grade,
            sub_grade,
            emp_title,
            emp_length,
            home_ownership,
            annual_inc,
            verification_status,
            addr_state,
            dti,
            delinq_2yrs,
            fico_range_low,
            fico_range_high,
            inq_last_6mths,
            open_acc,
            pub_rec,
            revol_bal,
            revol_util,
            total_acc,
            issue_d,
            loan_status,
            purpose,
            application_type,
            initial_list_status,
            out_prncp,
            total_pymnt,
            total_rec_prncp,
            total_rec_int,
            total_rec_late_fee,
            recoveries,
            collection_recovery_fee,
            last_pymnt_d,
            last_pymnt_amnt,
            fico_score
        )
        """

        print("\nLoading data into staging table...")

        cursor.execute(load_sql)

        connection.commit()

        # -----------------------------------------------------
        # Verify row count
        # -----------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM staging_loan_data"
        )

        row_count = cursor.fetchone()[0]

        print(
            f"\nRows loaded into staging: "
            f"{row_count:,}"
        )

        if row_count == 0:
            raise RuntimeError(
                "Staging load completed but no rows were loaded."
            )

        print("\n✓ Staging load completed successfully.")

        return row_count

    except Exception:

        connection.rollback()

        print(
            "\n✗ Staging load failed. "
            "Transaction rolled back."
        )

        raise

    finally:

        cursor.close()
        connection.close()


# -------------------------------------------------------------
# Standalone execution
# -------------------------------------------------------------

if __name__ == "__main__":

    load_to_staging()