# System Architecture

## Overview

The Credit Risk Data Engineering & Analytics Platform is an end-to-end data pipeline that transforms raw Lending Club loan data into a structured analytical data warehouse.

## Architecture

Raw Lending Club CSV
        |
        v
Python / Pandas
        |
        | Ingestion
        | Validation
        | Cleaning
        | Transformation
        v
MySQL Staging Layer
        |
        v
ETL Processing
        |
        v
MySQL Data Warehouse
        |
        v
Star Schema
        |
        v
SQL Analytics
        |
        v
Power BI

## Main Components

### 1. Source Layer

The source is the Lending Club accepted loans dataset.

The raw dataset contains approximately 2.26 million loan records and 151 columns.

### 2. Processing Layer

Python and Pandas are used for:

- Data ingestion
- Data profiling
- Data-quality checks
- Missing-value handling
- Data-type conversion
- Data standardization
- Business-rule validation
- Feature derivation

### 3. Staging Layer

The cleaned dataset is loaded into MySQL staging.

Table:

`staging_loan_data`

The staging layer provides a structured intermediate layer between the source data and warehouse.

### 4. Data Warehouse

The warehouse follows a star-schema design.

Fact table:

`fact_loan`

Dimension tables:

- `dim_date`
- `dim_loan`
- `dim_borrower`
- `dim_credit_profile`
- `dim_geography`

### 5. Analytics Layer

SQL queries are used to calculate business metrics related to:

- Loan volume
- Funding
- Credit risk
- Charge-offs
- Interest
- Outstanding principal
- Geography
- Loan grades
- Borrower characteristics