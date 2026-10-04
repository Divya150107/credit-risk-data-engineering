import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


# =============================================================
# IMPORT PIPELINE FUNCTIONS
# =============================================================

from src.ingestion.ingest_and_validate import (
    load_raw_data,
    run_ingestion_validation
)

from src.cleaning.clean_lending_data import (
    run_cleaning
)

from src.ingestion.load_to_mysql import (
    load_to_staging
)

from src.ingestion.load_large_dimensions import (
    load_dimensions
)

from src.ingestion.load_fact_loan import (
    load_fact_table
)

from src.validation.validate_fact_loan import (
    validate_fact_table
)

from src.validation.validate_loan_status import (
    validate_loan_status
)


# =============================================================
# PROJECT CONFIGURATION
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "lending_club_cleaned.csv"
)


# =============================================================
# LOAD ENVIRONMENT VARIABLES
# =============================================================

load_dotenv(
    PROJECT_ROOT / ".env"
)


# =============================================================
# MYSQL CONFIGURATION
# =============================================================

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}


# =============================================================
# DATABASE CONNECTION
# =============================================================

def get_database_connection():
    """
    Create a connection to the configured MySQL database.
    """

    return mysql.connector.connect(
        **DB_CONFIG
    )


def get_mysql_server_connection():
    """
    Create a MySQL connection without selecting a database.

    This is used when creating the database itself.
    """

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD")
    )


# =============================================================
# EXECUTE SQL SCRIPT
# =============================================================

def run_sql_script(
    script_path,
    use_database=True
):
    """
    Execute a SQL setup script.

    Parameters
    ----------
    script_path : Path
        Path to the SQL script.

    use_database : bool
        If True, connect to the configured database.
        If False, connect only to the MySQL server.
    """

    print(
        f"\nExecuting SQL setup script:"
    )

    print(
        f"{script_path}"
    )

    # ---------------------------------------------------------
    # Create appropriate connection
    # ---------------------------------------------------------

    if use_database:

        connection = get_database_connection()

    else:

        connection = get_mysql_server_connection()

    cursor = connection.cursor()

    try:

        # -----------------------------------------------------
        # Read SQL script
        # -----------------------------------------------------

        with open(
            script_path,
            "r",
            encoding="utf-8"
        ) as file:

            sql_script = file.read()

        # -----------------------------------------------------
        # Split script into individual SQL statements
        # -----------------------------------------------------

        statements = [
            statement.strip()
            for statement in sql_script.split(";")
            if statement.strip()
        ]

        # -----------------------------------------------------
        # Execute each statement
        # -----------------------------------------------------

        for statement in statements:

            cursor.execute(
                statement
            )

        # -----------------------------------------------------
        # Commit changes
        # -----------------------------------------------------

        connection.commit()

        print(
            "SQL setup completed successfully."
        )

    finally:

        cursor.close()
        connection.close()


# =============================================================
# DATABASE SETUP
# =============================================================

def setup_database():
    """
    Create the database, staging table and warehouse tables
    if they do not already exist.

    The SQL scripts use IF NOT EXISTS, so existing tables
    and data are not deleted or recreated.
    """

    setup_path = (
        PROJECT_ROOT
        / "sql"
        / "setup"
    )

    # ---------------------------------------------------------
    # STEP 1: CREATE DATABASE
    # ---------------------------------------------------------

    database_script = (
        setup_path
        / "01_create_database.sql"
    )

    run_sql_script(
        database_script,
        use_database=False
    )

    # ---------------------------------------------------------
    # STEP 2: CREATE STAGING TABLE
    # ---------------------------------------------------------

    staging_script = (
        setup_path
        / "02_create_staging.sql"
    )

    run_sql_script(
        staging_script,
        use_database=True
    )

    # ---------------------------------------------------------
    # STEP 3: CREATE WAREHOUSE TABLES
    # ---------------------------------------------------------

    warehouse_script = (
        setup_path
        / "03_create_warehouse.sql"
    )

    run_sql_script(
        warehouse_script,
        use_database=True
    )


# =============================================================
# CHECK PROCESSED DATA
# =============================================================

def processed_data_exists():

    return PROCESSED_DATA_PATH.exists()


# =============================================================
# CHECK STAGING TABLE
# =============================================================

def staging_data_exists():

    connection = get_database_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM staging_loan_data
            """
        )

        count = cursor.fetchone()[0]

        return count > 0

    finally:

        cursor.close()
        connection.close()


# =============================================================
# CHECK DIMENSION TABLES
# =============================================================

def dimensions_exist():

    connection = get_database_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dim_loan
            """
        )

        loan_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dim_borrower
            """
        )

        borrower_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dim_credit_profile
            """
        )

        credit_count = cursor.fetchone()[0]

        return (
            loan_count > 0
            and borrower_count > 0
            and credit_count > 0
        )

    finally:

        cursor.close()
        connection.close()


# =============================================================
# CHECK FACT TABLE
# =============================================================

def fact_table_exists():

    connection = get_database_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM fact_loan
            """
        )

        count = cursor.fetchone()[0]

        return count > 0

    finally:

        cursor.close()
        connection.close()


# =============================================================
# MAIN PIPELINE
# =============================================================

def run_pipeline():

    print(
        "\n" + "=" * 70
    )

    print(
        "CREDIT RISK DATA ENGINEERING PIPELINE"
    )

    print(
        "=" * 70
    )

    try:

        # =====================================================
        # DATABASE SETUP
        # =====================================================

        print(
            "\n" + "-" * 70
        )

        print(
            "DATABASE SETUP"
        )

        print(
            "-" * 70
        )

        setup_database()


        # =====================================================
        # STEP 1 & 2: RAW INGESTION + VALIDATION
        # =====================================================

        if processed_data_exists():

            print(
                "\n" + "-" * 70
            )

            print(
                "PROCESSED DATA ALREADY EXISTS"
            )

            print(
                "-" * 70
            )

            print(
                f"Found:\n{PROCESSED_DATA_PATH}"
            )

            print(
                "\nSkipping raw ingestion and cleaning."
            )

        else:

            print(
                "\n" + "-" * 70
            )

            print(
                "PROCESSED DATA NOT FOUND"
            )

            print(
                "-" * 70
            )

            print(
                "\nRunning raw data ingestion..."
            )

            raw_df = load_raw_data()

            print(
                "\nRunning raw data validation..."
            )

            run_ingestion_validation(
                raw_df
            )

            # =================================================
            # STEP 3: CLEANING
            # =================================================

            print(
                "\nRunning data cleaning and transformation..."
            )

            run_cleaning(
                raw_df
            )


        # =====================================================
        # STEP 4: STAGING
        # =====================================================

        if staging_data_exists():

            print(
                "\n" + "-" * 70
            )

            print(
                "STAGING DATA ALREADY EXISTS"
            )

            print(
                "-" * 70
            )

            print(
                "Skipping staging load."
            )

        else:

            print(
                "\n" + "-" * 70
            )

            print(
                "STAGING DATA NOT FOUND"
            )

            print(
                "-" * 70
            )

            print(
                "\nLoading processed data into staging..."
            )

            load_to_staging()


        # =====================================================
        # STEP 5: DIMENSIONS
        # =====================================================

        if dimensions_exist():

            print(
                "\n" + "-" * 70
            )

            print(
                "DIMENSIONS ALREADY EXIST"
            )

            print(
                "-" * 70
            )

            print(
                "Skipping dimension loading."
            )

        else:

            print(
                "\n" + "-" * 70
            )

            print(
                "DIMENSIONS NOT FOUND"
            )

            print(
                "-" * 70
            )

            print(
                "\nLoading dimension tables..."
            )

            load_dimensions()


        # =====================================================
        # STEP 6: FACT TABLE
        # =====================================================

        if fact_table_exists():

            print(
                "\n" + "-" * 70
            )

            print(
                "FACT TABLE ALREADY EXISTS"
            )

            print(
                "-" * 70
            )

            print(
                "Skipping fact-table loading."
            )

        else:

            print(
                "\n" + "-" * 70
            )

            print(
                "FACT TABLE NOT FOUND"
            )

            print(
                "-" * 70
            )

            print(
                "\nLoading fact table..."
            )

            load_fact_table()


        # =====================================================
        # STEP 7: FACT RECONCILIATION
        # =====================================================

        print(
            "\n" + "-" * 70
        )

        print(
            "RUNNING FACT TABLE RECONCILIATION"
        )

        print(
            "-" * 70
        )

        validate_fact_table()


        # =====================================================
        # STEP 8: LOAN STATUS RECONCILIATION
        # =====================================================

        print(
            "\n" + "-" * 70
        )

        print(
            "RUNNING LOAN STATUS RECONCILIATION"
        )

        print(
            "-" * 70
        )

        validate_loan_status()


        # =====================================================
        # PIPELINE SUCCESS
        # =====================================================

        print(
            "\n" + "=" * 70
        )

        print(
            "PIPELINE COMPLETED SUCCESSFULLY"
        )

        print(
            "=" * 70
        )

        print(
            "\nPipeline status:"
        )

        print(
            "✓ Database setup checked"
        )

        print(
            "✓ Processed data checked"
        )

        print(
            "✓ Staging checked"
        )

        print(
            "✓ Dimensions checked"
        )

        print(
            "✓ Fact table checked"
        )

        print(
            "✓ Fact reconciliation passed"
        )

        print(
            "✓ Loan-status reconciliation passed"
        )


    except Exception as error:

        print(
            "\n" + "=" * 70
        )

        print(
            "PIPELINE FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {error}"
        )

        raise


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":

    run_pipeline()