import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "accepted_2007_to_2018Q4.csv.gz"
)


# ---------------------------------------------------------
# 1. Load raw data
# ---------------------------------------------------------

def load_raw_data():
    """
    Load the raw Lending Club dataset.

    Returns
    -------
    pandas.DataFrame
        Raw Lending Club dataset.
    """

    print("\n" + "=" * 60)
    print("STEP 1: RAW DATA INGESTION")
    print("=" * 60)

    print(f"Reading file: {RAW_DATA_PATH}")

    df = pd.read_csv(
        RAW_DATA_PATH,
        low_memory=False
    )

    print(
        f"Raw dataset loaded successfully: "
        f"{len(df):,} rows × {len(df.columns):,} columns"
    )

    return df


# ---------------------------------------------------------
# 2. Validate required schema
# ---------------------------------------------------------

def validate_schema(df):
    """
    Validate that required business columns exist.
    """

    required_columns = [
        "id",
        "loan_amnt",
        "funded_amnt",
        "funded_amnt_inv",
        "term",
        "int_rate",
        "installment",
        "grade",
        "sub_grade",
        "emp_length",
        "home_ownership",
        "annual_inc",
        "verification_status",
        "issue_d",
        "loan_status",
        "purpose",
        "addr_state",
        "dti",
        "fico_range_low",
        "fico_range_high",
        "revol_util",
        "total_pymnt",
        "total_rec_prncp",
        "total_rec_int",
        "recoveries"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Schema validation failed. "
            f"Missing columns: {missing_columns}"
        )

    print("✓ Required-column validation passed.")

    return True


# ---------------------------------------------------------
# 3. Validate duplicates
# ---------------------------------------------------------

def validate_duplicates(df):
    """
    Check duplicate rows and duplicate loan IDs.
    """

    duplicate_rows = df.duplicated().sum()

    duplicate_ids = df["id"].duplicated().sum()

    print(f"Duplicate rows: {duplicate_rows:,}")
    print(f"Duplicate loan IDs: {duplicate_ids:,}")

    if duplicate_rows > 0:

        print(
            "WARNING: Duplicate complete rows detected."
        )

    if duplicate_ids > 0:

        print(
            "WARNING: Duplicate loan IDs detected."
        )

    return {
        "duplicate_rows": duplicate_rows,
        "duplicate_ids": duplicate_ids
    }


# ---------------------------------------------------------
# 4. Validate business rules
# ---------------------------------------------------------

def validate_business_rules(df):
    """
    Run numerical and business-rule validation checks.
    """

    checks = {

        "Annual income <= 0":
            (df["annual_inc"] <= 0).sum(),

        "Negative DTI":
            (df["dti"] < 0).sum(),

        "DTI = 999":
            (df["dti"] == 999).sum(),

        "Revol util > 100":
            (df["revol_util"] > 100).sum(),

        "Interest rate <= 0":
            (df["int_rate"] <= 0).sum(),

        "Installment <= 0":
            (df["installment"] <= 0).sum(),

        "FICO low < 300":
            (df["fico_range_low"] < 300).sum(),

        "FICO high > 850":
            (df["fico_range_high"] > 850).sum(),

        "FICO low > FICO high":
            (
                df["fico_range_low"]
                > df["fico_range_high"]
            ).sum(),

        "Funded amount > loan amount":
            (
                df["funded_amnt"]
                > df["loan_amnt"]
            ).sum(),

        "Investor funded > funded":
            (
                df["funded_amnt_inv"]
                > df["funded_amnt"]
            ).sum()
    }

    print("\nBusiness-rule validation:")

    for check_name, count in checks.items():

        print(
            f"{check_name:<35}: {count:,}"
        )

    return checks


# ---------------------------------------------------------
# 5. Complete ingestion + validation stage
# ---------------------------------------------------------

def run_ingestion_validation(df):
    """
    Run all raw-data validation checks.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw Lending Club dataset.

    Returns
    -------
    pandas.DataFrame
        Validated raw dataset.
    """

    print("\n" + "=" * 60)
    print("RAW DATA VALIDATION")
    print("=" * 60)

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns):,}"
    )

    # Schema validation
    validate_schema(df)

    # Duplicate validation
    validate_duplicates(df)

    # Business-rule validation
    validate_business_rules(df)

    print("\n✓ Raw data validation completed.")

    return df


# ---------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------

if __name__ == "__main__":

    df = load_raw_data()

    run_ingestion_validation(df)