# ETL Pipeline Documentation

## Objective

The objective of the pipeline is to transform raw Lending Club data into a clean, structured and analytics-ready data warehouse.

## ETL Flow

Raw CSV
    ↓
Ingestion
    ↓
Validation
    ↓
Cleaning
    ↓
Transformation
    ↓
MySQL Staging
    ↓
Warehouse Loading
    ↓
Validation
    ↓
Analytics

## 1. Ingestion

The raw Lending Club CSV file is read using Pandas.

Source:

`accepted_2007_to_2018Q4.csv.gz`

The original dataset contains:

- 2,260,701 rows
- 151 columns

## 2. Column Selection

Only business-relevant columns are retained.

The selected fields cover:

- Loan information
- Borrower information
- Credit information
- Loan classification
- Loan performance

## 3. Data Cleaning

The following cleaning operations are performed:

### Duplicate Records

Duplicate loan IDs are checked and removed where applicable.

### Missing Loan IDs

Records without a loan ID are removed because the loan ID is required as the business key.

### Loan Term

Loan term values are converted into numeric months.

### Interest Rate

Interest rates are converted from percentage values into decimal representation.

Example:

`10.5% → 0.105`

### Employment Length

Employment length values such as:

- `< 1 year`
- `2 years`
- `10+ years`

are converted into numeric years.

### Annual Income

Non-positive annual income values are treated as invalid and converted to null.

### DTI

Invalid negative DTI values and the special value `999` are treated as invalid.

### Revolving Utilization

Values outside the valid 0–100 percentage range are treated as invalid.

The resulting value is stored in decimal form.

### FICO Score

A single FICO score is derived from:

`(fico_range_low + fico_range_high) / 2`

### Dates

Loan issue dates and last-payment dates are converted into proper date values.

### Loan Status

Long credit-policy status descriptions are normalized into standard categories such as:

- Fully Paid
- Charged Off

## 4. Staging

The cleaned data is loaded into:

`staging_loan_data`

The staging table contains 2,260,668 records.

## 5. Warehouse Transformation

The staging data is transformed into a star-schema warehouse consisting of:

- `dim_date`
- `dim_loan`
- `dim_borrower`
- `dim_credit_profile`
- `dim_geography`
- `fact_loan`

## 6. Validation

The warehouse is validated against the staging layer.

Validation includes:

- Row-count reconciliation
- Duplicate checks
- Foreign-key validation
- Financial reconciliation
- Loan-level reconciliation
- Loan-status reconciliation

All major reconciliation checks completed successfully with zero mismatches.