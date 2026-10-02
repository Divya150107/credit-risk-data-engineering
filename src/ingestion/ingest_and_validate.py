import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "accepted_2007_to_2018Q4.csv.gz"
)


# ============================================================
# LOAD RAW DATA
# ============================================================

print("Loading Lending Club dataset...")

df = pd.read_csv(
    DATA_PATH,
    low_memory=False
)

print("Dataset loaded successfully.")


# ============================================================
# 1. DATASET OVERVIEW
# ============================================================

print("\n" + "=" * 60)
print("1. DATASET OVERVIEW")
print("=" * 60)

print(f"Rows              : {len(df):,}")
print(f"Columns           : {len(df.columns):,}")
print(f"Memory usage (MB) : {df.memory_usage(deep=True).sum() / 1024**2:,.2f}")


# ============================================================
# 2. SCHEMA VALIDATION
# ============================================================

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
    col for col in required_columns
    if col not in df.columns
]

print("\n" + "=" * 60)
print("2. SCHEMA VALIDATION")
print("=" * 60)

if missing_columns:
    print("FAILED")
    print("Missing required columns:")
    print(missing_columns)
else:
    print("PASSED - All required business columns are present.")


# ============================================================
# 3. UNIQUENESS VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("3. UNIQUENESS VALIDATION")
print("=" * 60)

duplicate_rows = df.duplicated().sum()
duplicate_ids = df["id"].duplicated().sum()

print(f"Duplicate rows : {duplicate_rows:,}")
print(f"Duplicate IDs  : {duplicate_ids:,}")

if duplicate_rows == 0 and duplicate_ids == 0:
    print("PASSED - No duplicate records or loan IDs.")
else:
    print("WARNING - Duplicate records detected.")


# ============================================================
# 4. MISSING VALUE ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("4. MISSING VALUE ANALYSIS")
print("=" * 60)

missing_count = df.isna().sum()

missing_percentage = (
    missing_count
    .div(len(df))
    .mul(100)
    .round(2)
)

missing_report = pd.DataFrame({
    "missing_count": missing_count,
    "missing_percentage": missing_percentage
})

missing_report = (
    missing_report
    .sort_values("missing_percentage", ascending=False)
)

print("\nTop 20 columns by missing percentage:")
print(missing_report.head(20))


# Completely empty columns
empty_columns = [
    col
    for col in df.columns
    if df[col].isna().all()
]

print("\nCompletely empty columns:")
print(empty_columns)


# ============================================================
# 5. LOAN STATUS VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("5. LOAN STATUS VALIDATION")
print("=" * 60)

loan_status_distribution = (
    df["loan_status"]
    .value_counts(dropna=False)
)

print(loan_status_distribution)

print(
    "\nMissing loan status:",
    df["loan_status"].isna().sum()
)


# ============================================================
# 6. NUMERICAL BUSINESS RULE VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("6. NUMERICAL BUSINESS RULE VALIDATION")
print("=" * 60)

validation_checks = {

    "Loan amount <= 0":
        (df["loan_amnt"] <= 0).sum(),

    "Funded amount <= 0":
        (df["funded_amnt"] <= 0).sum(),

    "Annual income <= 0":
        (df["annual_inc"] <= 0).sum(),

    "Negative DTI":
        (df["dti"] < 0).sum(),

    "DTI = 999":
        (df["dti"] == 999).sum(),

    "Interest rate <= 0":
        (df["int_rate"] <= 0).sum(),

    "Installment <= 0":
        (df["installment"] <= 0).sum(),

    "Revol utilization < 0":
        (df["revol_util"] < 0).sum(),

    "Revol utilization > 100":
        (df["revol_util"] > 100).sum(),

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

    "Funded investor amount > funded amount":
        (
            df["funded_amnt_inv"]
            > df["funded_amnt"]
        ).sum(),

}

for check, count in validation_checks.items():
    print(f"{check:<40}: {count:,}")


# ============================================================
# 7. CATEGORICAL VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("7. CATEGORICAL VALIDATION")
print("=" * 60)

print("\nLoan grades:")
print(df["grade"].value_counts(dropna=False))

print("\nLoan terms:")
print(df["term"].value_counts(dropna=False))

print("\nHome ownership:")
print(df["home_ownership"].value_counts(dropna=False))

print("\nVerification status:")
print(df["verification_status"].value_counts(dropna=False))

print("\nApplication type:")
print(df["application_type"].value_counts(dropna=False))

print("\nPurpose:")
print(df["purpose"].value_counts(dropna=False).head(20))


# ============================================================
# 8. DATE VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("8. DATE VALIDATION")
print("=" * 60)

date_columns = [
    "issue_d",
    "earliest_cr_line",
    "last_pymnt_d",
    "next_pymnt_d",
    "last_credit_pull_d"
]

for column in date_columns:

    if column in df.columns:

        parsed_dates = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        invalid_dates = (
            df[column].notna()
            & parsed_dates.isna()
        ).sum()

        print(
            f"{column:<25}: "
            f"invalid dates = {invalid_dates:,}"
        )


# ============================================================
# 9. IMPORTANT NULL CHECKS
# ============================================================

print("\n" + "=" * 60)
print("9. IMPORTANT BUSINESS FIELD NULLS")
print("=" * 60)

important_fields = [
    "id",
    "loan_amnt",
    "funded_amnt",
    "int_rate",
    "grade",
    "annual_inc",
    "loan_status",
    "issue_d",
    "purpose",
    "addr_state"
]

for column in important_fields:

    missing = df[column].isna().sum()

    percentage = (
        missing / len(df) * 100
    )

    print(
        f"{column:<25}: "
        f"{missing:,} "
        f"({percentage:.2f}%)"
    )


# ============================================================
# 10. VALIDATION SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("10. VALIDATION SUMMARY")
print("=" * 60)

print(f"""
Dataset
-------
Rows                  : {len(df):,}
Columns               : {len(df.columns):,}

Uniqueness
----------
Duplicate rows        : {duplicate_rows:,}
Duplicate loan IDs    : {duplicate_ids:,}

Major quality issues
--------------------
Completely empty cols : {len(empty_columns)}
Missing loan status   : {df["loan_status"].isna().sum():,}
Invalid annual income : {(df["annual_inc"] <= 0).sum():,}
Negative DTI          : {(df["dti"] < 0).sum():,}
DTI = 999             : {(df["dti"] == 999).sum():,}
Revol util > 100      : {(df["revol_util"] > 100).sum():,}

Validation complete.
Raw data has NOT been modified.
""")