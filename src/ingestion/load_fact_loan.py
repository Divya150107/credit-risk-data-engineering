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
# LOAD DIMENSION MAPPINGS
# ============================================================

print("\nLoading dimension mappings...")


# ------------------------------------------------------------
# Loan dimension
# ------------------------------------------------------------

cursor.execute(
    """
    SELECT loan_id, loan_key
    FROM dim_loan
    """
)

loan_map = {
    loan_id: loan_key
    for loan_id, loan_key in cursor.fetchall()
}

print(f"dim_loan mappings      : {len(loan_map):,}")


# ------------------------------------------------------------
# Borrower dimension
# ------------------------------------------------------------

cursor.execute(
    """
    SELECT loan_id, borrower_key
    FROM dim_borrower
    """
)

borrower_map = {
    loan_id: borrower_key
    for loan_id, borrower_key in cursor.fetchall()
}

print(f"dim_borrower mappings  : {len(borrower_map):,}")


# ------------------------------------------------------------
# Credit profile dimension
# ------------------------------------------------------------

cursor.execute(
    """
    SELECT loan_id, credit_profile_key
    FROM dim_credit_profile
    """
)

credit_map = {
    loan_id: credit_profile_key
    for loan_id, credit_profile_key in cursor.fetchall()
}

print(f"dim_credit_profile mappings : {len(credit_map):,}")


# ------------------------------------------------------------
# Geography dimension
# ------------------------------------------------------------

cursor.execute(
    """
    SELECT state_code, geography_key
    FROM dim_geography
    """
)

geography_map = {
    state_code: geography_key
    for state_code, geography_key in cursor.fetchall()
}

print(f"dim_geography mappings : {len(geography_map):,}")


# ============================================================
# LOAD FACT TABLE
# ============================================================

print("\nLoading fact_loan...")


last_id = ""

total_loaded = 0


while True:

    # --------------------------------------------------------
    # Fetch next batch
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            addr_state,
            issue_d,
            loan_status,
            loan_amnt,
            funded_amnt,
            funded_amnt_inv,
            int_rate,
            installment,
            out_prncp,
            total_pymnt,
            total_rec_prncp,
            total_rec_int,
            total_rec_late_fee,
            recoveries,
            collection_recovery_fee,
            last_pymnt_d,
            last_pymnt_amnt

        FROM staging_loan_data

        WHERE id > %s

        ORDER BY id

        LIMIT %s
        """,
        (last_id, BATCH_SIZE)
    )

    rows = cursor.fetchall()


    # --------------------------------------------------------
    # Stop when finished
    # --------------------------------------------------------

    if not rows:
        break


    fact_rows = []


    # ========================================================
    # Transform batch
    # ========================================================

    for row in rows:

        (
            loan_id,
            state_code,
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


        # ----------------------------------------------------
        # Dimension keys
        # ----------------------------------------------------

        loan_key = loan_map[loan_id]

        borrower_key = borrower_map[loan_id]

        credit_profile_key = credit_map[loan_id]

        geography_key = geography_map[state_code]


        # ----------------------------------------------------
        # Date key
        # ----------------------------------------------------

        if issue_date is not None:

            issue_date_key = int(
                issue_date.strftime("%Y%m%d")
            )

        else:

            issue_date_key = None


        # ----------------------------------------------------
        # Add fact record
        # ----------------------------------------------------

        fact_rows.append(
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


    # ========================================================
    # Insert batch
    # ========================================================

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
        fact_rows
    )


    # --------------------------------------------------------
    # Commit batch
    # --------------------------------------------------------

    connection.commit()


    # --------------------------------------------------------
    # Update progress
    # --------------------------------------------------------

    total_loaded += len(rows)

    last_id = rows[-1][0]

    print(
        f"Loaded {total_loaded:,} fact records..."
    )


# ============================================================
# VERIFY
# ============================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM fact_loan
    """
)

fact_count = cursor.fetchone()[0]


print("\n============================================================")
print("FACT TABLE LOAD COMPLETE")
print("============================================================")
print(f"fact_loan rows : {fact_count:,}")


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nMySQL connection closed.")