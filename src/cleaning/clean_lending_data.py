import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "accepted_2007_to_2018Q4.csv.gz"
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PATH = (
    PROCESSED_DIR
    / "lending_club_cleaned.csv"
)


# ============================================================
# 2. LOAD RAW DATA
# ============================================================

print("Loading raw Lending Club dataset...")

df = pd.read_csv(
    RAW_DATA_PATH,
    low_memory=False
)

print("Raw shape:", df.shape)


# ============================================================
# 3. SELECT BUSINESS-RELEVANT COLUMNS
# ============================================================

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

    # Credit profile
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

    # Loan information / classification
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

print("After column selection:", df.shape)


# ============================================================
# 4. STANDARDIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.lower()
    .str.strip()
)


# ============================================================
# 5. REMOVE RECORDS WITH MISSING CORE LOAN INFORMATION
# ============================================================

core_columns = [
    "id",
    "loan_amnt",
    "funded_amnt",
    "int_rate",
    "grade",
    "loan_status",
    "issue_d",
    "purpose"
]

before = len(df)

df = df.dropna(
    subset=core_columns
)

after = len(df)

print(
    f"Removed {before - after:,} "
    "records with missing core loan information."
)


# ============================================================
# 6. REMOVE DUPLICATES
# ============================================================

before = len(df)

df = df.drop_duplicates(
    subset=["id"]
)

after = len(df)

print(
    f"Removed {before - after:,} duplicate loan IDs."
)


# ============================================================
# 7. CLEAN TERM
# ============================================================

df["term"] = (
    df["term"]
    .str.extract(r"(\d+)")
    .astype("Int64")
)


# ============================================================
# 8. CLEAN INTEREST RATE
# ============================================================

df["int_rate"] = (
    pd.to_numeric(
        df["int_rate"],
        errors="coerce"
    )
)


# Convert percentage to decimal
# Example: 10.5 -> 0.105

df["int_rate"] = df["int_rate"] / 100


# ============================================================
# 9. CLEAN EMPLOYMENT LENGTH
# ============================================================

df["emp_length"] = (
    df["emp_length"]
    .astype("string")
    .str.extract(r"(\d+)")[0]
)

df["emp_length"] = pd.to_numeric(
    df["emp_length"],
    errors="coerce"
)


# ============================================================
# 10. CLEAN ANNUAL INCOME
# ============================================================

df.loc[
    df["annual_inc"] <= 0,
    "annual_inc"
] = np.nan


# ============================================================
# 11. CLEAN DTI
# ============================================================

df.loc[
    (df["dti"] < 0) |
    (df["dti"] == 999),
    "dti"
] = np.nan


# ============================================================
# 12. CLEAN REVOLVING UTILIZATION
# ============================================================

df.loc[
    (df["revol_util"] < 0) |
    (df["revol_util"] > 100),
    "revol_util"
] = np.nan


# Convert percentage to decimal

df["revol_util"] = (
    df["revol_util"] / 100
)


# ============================================================
# 13. CREATE FICO SCORE
# ============================================================

df["fico_score"] = (
    df["fico_range_low"] +
    df["fico_range_high"]
) / 2


# ============================================================
# 14. STANDARDIZE DATES
# ============================================================

date_columns = [
    "issue_d",
    "last_pymnt_d"
]

for column in date_columns:

    df[column] = pd.to_datetime(
        df[column],
        format="%b-%Y",
        errors="coerce"
    )


# ============================================================
# 15. STANDARDIZE LOAN STATUS
# ============================================================

df["loan_status"] = (
    df["loan_status"]
    .replace({
        "Does not meet the credit policy. Status:Fully Paid":
            "Fully Paid",

        "Does not meet the credit policy. Status:Charged Off":
            "Charged Off"
    })
)


# ============================================================
# 16. STANDARDIZE TEXT COLUMNS
# ============================================================

text_columns = [
    "grade",
    "sub_grade",
    "emp_title",
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


# ============================================================
# 17. FINAL DATA QUALITY CHECKS
# ============================================================

print("\n========== FINAL QUALITY CHECK ==========")

print("Final shape:", df.shape)

print(
    "Duplicate loan IDs:",
    df["id"].duplicated().sum()
)

print(
    "Missing loan IDs:",
    df["id"].isna().sum()
)

print(
    "Invalid annual income:",
    (df["annual_inc"] <= 0).sum()
)

print(
    "Invalid DTI:",
    (
        (df["dti"] < 0) |
        (df["dti"] == 999)
    ).sum()
)

print(
    "Invalid revol_util:",
    (
        (df["revol_util"] < 0) |
        (df["revol_util"] > 1)
    ).sum()
)


# ============================================================
# 18. SAVE PROCESSED DATA
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n========== CLEANING COMPLETE ==========")

print(
    "Processed dataset saved to:"
)

print(OUTPUT_PATH)