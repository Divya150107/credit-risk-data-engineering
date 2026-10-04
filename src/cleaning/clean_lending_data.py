import pandas as pd
from pathlib import Path


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
# Clean and transform Lending Club data
# -------------------------------------------------------------

def clean_lending_data(df):
    """
    Clean and transform the raw Lending Club dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw Lending Club dataset.

    Returns
    -------
    pandas.DataFrame
        Cleaned and transformed dataset.
    """

    print("\n" + "=" * 60)
    print("STEP 2: DATA CLEANING & TRANSFORMATION")
    print("=" * 60)

    print(f"Input shape: {df.shape}")

    # ---------------------------------------------------------
    # 1. Select business-relevant columns
    # ---------------------------------------------------------

    selected_columns = [

        # Loan information
        "id",
        "loan_amnt",
        "funded_amnt",
        "funded_amnt_inv",
        "term",
        "int_rate",
        "installment",
        "grade",
        "sub_grade",

        # Borrower information
        "emp_title",
        "emp_length",
        "home_ownership",
        "annual_inc",
        "verification_status",
        "addr_state",

        # Credit information
        "dti",
        "delinq_2yrs",
        "fico_range_low",
        "fico_range_high",
        "inq_last_6mths",
        "open_acc",
        "pub_rec",
        "revol_bal",
        "revol_util",
        "total_acc",

        # Classification
        "issue_d",
        "loan_status",
        "purpose",
        "application_type",
        "initial_list_status",

        # Loan performance
        "out_prncp",
        "total_pymnt",
        "total_rec_prncp",
        "total_rec_int",
        "total_rec_late_fee",
        "recoveries",
        "collection_recovery_fee",
        "last_pymnt_d",
        "last_pymnt_amnt"
    ]

    df = df[selected_columns].copy()

    print(
        f"After column selection: "
        f"{df.shape}"
    )

    # ---------------------------------------------------------
    # 2. Remove records with missing critical loan information
    # ---------------------------------------------------------

    critical_columns = [
        "id",
        "loan_amnt",
        "funded_amnt",
        "funded_amnt_inv",
        "loan_status",
        "issue_d"
    ]

    before = len(df)

    df = df.dropna(
        subset=critical_columns
    )

    removed = before - len(df)

    print(
        f"Rows removed due to missing "
        f"critical fields: {removed:,}"
    )

    # ---------------------------------------------------------
    # 3. Remove duplicate loan IDs
    # ---------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates(
        subset=["id"]
    )

    removed = before - len(df)

    print(
        f"Duplicate loan IDs removed: "
        f"{removed:,}"
    )

    # ---------------------------------------------------------
    # 4. Clean loan term
    #
    # Example:
    # "36 months" → 36
    # "60 months" → 60
    # ---------------------------------------------------------

    df["term"] = (
        df["term"]
        .astype("string")
        .str.extract(r"(\d+)")[0]
    )

    df["term"] = pd.to_numeric(
        df["term"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 5. Convert interest rate
    #
    # Example:
    # 13.56 → 0.1356
    # ---------------------------------------------------------

    df["int_rate"] = pd.to_numeric(
        df["int_rate"],
        errors="coerce"
    ) / 100

    # ---------------------------------------------------------
    # 6. Clean employment length
    #
    # Examples:
    # "10+ years" → 10
    # "2 years"   → 2
    # "< 1 year"  → 1
    # ---------------------------------------------------------

    df["emp_length"] = (
        df["emp_length"]
        .astype("string")
        .str.extract(r"(\d+)")[0]
    )

    df["emp_length"] = pd.to_numeric(
        df["emp_length"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 7. Clean annual income
    #
    # Invalid values <= 0 are converted to NULL.
    # ---------------------------------------------------------

    df["annual_inc"] = pd.to_numeric(
        df["annual_inc"],
        errors="coerce"
    )

    df.loc[
        df["annual_inc"] <= 0,
        "annual_inc"
    ] = pd.NA

    # ---------------------------------------------------------
    # 8. Clean DTI
    #
    # Negative DTI and 999 are treated as invalid.
    # ---------------------------------------------------------

    df["dti"] = pd.to_numeric(
        df["dti"],
        errors="coerce"
    )

    df.loc[
        df["dti"] < 0,
        "dti"
    ] = pd.NA

    df.loc[
        df["dti"] == 999,
        "dti"
    ] = pd.NA

    # ---------------------------------------------------------
    # 9. Clean revolving utilization
    #
    # Valid range: 0–100
    #
    # Then convert percentage to decimal:
    # 50 → 0.50
    # ---------------------------------------------------------

    df["revol_util"] = pd.to_numeric(
        df["revol_util"],
        errors="coerce"
    )

    df.loc[
        (df["revol_util"] < 0) |
        (df["revol_util"] > 100),
        "revol_util"
    ] = pd.NA

    df["revol_util"] = (
        df["revol_util"] / 100
    )

    # ---------------------------------------------------------
    # 10. Create FICO score
    #
    # FICO score = average of low and high range.
    # ---------------------------------------------------------

    df["fico_score"] = (
        df["fico_range_low"] +
        df["fico_range_high"]
    ) / 2

    # ---------------------------------------------------------
    # 11. Convert issue date
    #
    # Example:
    # "Dec-2015" → 2015-12-01
    # ---------------------------------------------------------

    df["issue_d"] = pd.to_datetime(
        df["issue_d"],
        format="%b-%Y",
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 12. Convert last payment date
    # ---------------------------------------------------------

    df["last_pymnt_d"] = pd.to_datetime(
        df["last_pymnt_d"],
        format="%b-%Y",
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 13. Normalize loan status
    # ---------------------------------------------------------

    df["loan_status"] = df[
        "loan_status"
    ].replace({

        "Does not meet the credit policy. Status:Fully Paid":
            "Fully Paid",

        "Does not meet the credit policy. Status:Charged Off":
            "Charged Off"
    })

    # ---------------------------------------------------------
    # 14. Standardize text columns
    # ---------------------------------------------------------

    text_columns = [
        "grade",
        "sub_grade",
        "home_ownership",
        "verification_status",
        "addr_state",
        "loan_status",
        "purpose",
        "application_type",
        "initial_list_status"
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # ---------------------------------------------------------
    # 15. Final validation
    # ---------------------------------------------------------

    print("\nFinal cleaning validation:")

    print(
        f"Missing loan IDs: "
        f"{df['id'].isna().sum():,}"
    )

    print(
        f"Duplicate loan IDs: "
        f"{df['id'].duplicated().sum():,}"
    )

    print(
        f"Invalid annual income: "
        f"{(df['annual_inc'] <= 0).sum():,}"
    )

    print(
        f"Invalid DTI: "
        f"{((df['dti'] < 0) | (df['dti'] == 999)).sum():,}"
    )

    print(
        f"Invalid revolving utilization: "
        f"{(
            (df['revol_util'] < 0) |
            (df['revol_util'] > 1)
        ).sum():,}"
    )

    print(
        f"\nFinal cleaned shape: "
        f"{df.shape}"
    )

    return df


# -------------------------------------------------------------
# Save cleaned dataset
# -------------------------------------------------------------

def save_cleaned_data(df):
    """
    Save cleaned dataset to the processed-data directory.
    """

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        PROCESSED_DATA_PATH,
        index=False
    )

    print(
        "\n✓ Cleaned dataset saved to:"
    )

    print(
        PROCESSED_DATA_PATH
    )


# -------------------------------------------------------------
# Main cleaning function for pipeline
# -------------------------------------------------------------

def run_cleaning(df):
    """
    Execute the complete cleaning process
    and save the processed dataset.
    """

    cleaned_df = clean_lending_data(df)

    save_cleaned_data(
        cleaned_df
    )

    return cleaned_df


# -------------------------------------------------------------
# Standalone execution
# -------------------------------------------------------------

if __name__ == "__main__":

    from src.ingestion.ingest_and_validate import (
        load_raw_data,
        run_ingestion_validation
    )

    # Load raw data
    raw_df = load_raw_data()

    # Validate raw data
    run_ingestion_validation(
        raw_df
    )

    # Clean and transform
    cleaned_df = run_cleaning(
        raw_df
    )

    print(
        "\n✓ Cleaning module completed successfully."
    )