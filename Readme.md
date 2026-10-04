# Credit Risk Data Engineering & Analytics Platform

## Overview

An end-to-end data engineering project that transforms approximately **2.26 million Lending Club loan records** into a validated MySQL analytical data warehouse.

The project demonstrates **Python-based ETL, data quality validation, data transformation, MySQL staging, dimensional modeling, batch loading, reconciliation, and SQL analytics**.

---

## Business Objective

Build a reliable lending data platform for analyzing:

- Loan portfolio volume and funding
- Charge-off rates and credit-risk patterns
- Interest and principal collections
- Outstanding principal
- Geographic funding distribution
- Loan origination trends

---

## Architecture

```text
Lending Club Raw CSV
        ↓
Python / Pandas
        ↓
Validation & Cleaning
        ↓
Processed Data
        ↓
MySQL Staging
        ↓
Star Schema Warehouse
        ↓
Reconciliation
        ↓
SQL Analytics
```

---

## Dataset

**Source:** Lending Club dataset from Kaggle

- Raw records: ~2.26 million
- Raw columns: 151
- Processed records: **2,260,668**
- Processed columns: **40**

Key cleaning operations include:

- Duplicate and data-quality validation
- Invalid income and DTI handling
- Revolving utilization validation
- FICO score derivation
- Date and categorical standardization
- Loan-status normalization

---

## Data Warehouse

The warehouse follows a **star schema**.

### Staging

```text
staging_loan_data
```

### Dimensions

```text
dim_date
dim_loan
dim_borrower
dim_credit_profile
dim_geography
```

### Fact

```text
fact_loan
```

The fact table stores loan-level financial measures and uses surrogate keys to connect to the dimension tables.

---

## Pipeline

The complete pipeline is executed using:

```bash
python run_pipeline.py
```

The pipeline automatically:

1. Creates the database and required tables if they do not exist.
2. Ingests and validates raw data when required.
3. Cleans and transforms the data.
4. Loads the MySQL staging layer.
5. Loads dimension tables.
6. Loads the fact table.
7. Performs financial reconciliation.
8. Performs loan-status reconciliation.

Existing processed data and populated warehouse tables are detected and skipped to avoid unnecessary reprocessing.

---

## SQL Setup

Database and warehouse definitions are maintained separately under:

```text
sql/setup/
├── 01_create_database.sql
├── 02_create_staging.sql
└── 03_create_warehouse.sql
```

The scripts use `IF NOT EXISTS` statements, making the setup non-destructive.

---

## Data Quality & Reconciliation

The pipeline validates data before loading and reconciles the staging and fact layers after loading.

Financial fields reconciled include:

- Loan amount
- Funded amount
- Investor-funded amount
- Total payment
- Principal received
- Interest received
- Recoveries

Final validation:

```text
Records checked       : 2,260,668
Financial mismatches  : 0
Loan-status mismatches: 0

STATUS: PASSED
```

---

## Technology Stack

- **Python**
- **Pandas / NumPy**
- **MySQL**
- **SQL**
- **Git / GitHub**

### Responsibilities

**Python:** ingestion, validation, cleaning, transformation, loading, orchestration

**SQL/MySQL:** database setup, staging, warehouse modeling, reconciliation, analytics

---

## Project Structure

```text
credit-risk-data-engineering/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
├── notebooks/
│
├── sql/
│   ├── analytics/
│   ├── setup/
│   ├── staging/
│   └── warehouse/
│
├── src/
│   ├── cleaning/
│   ├── ingestion/
│   ├── transformation/
│   └── validation/
│
├── .gitignore
├── README.md
├── requirements.txt
└── run_pipeline.py
```

---

## How to Run

### 1. Clone the Repository

```bash
git clone <repository-url>
cd credit-risk-data-engineering
```

### 2. Install Dependencies

```bash
python -m venv creditde
creditde\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure MySQL

Create a `.env` file:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=credit_risk_db
```

### 4. Add the Dataset

Place:

```text
accepted_2007_to_2018Q4.csv.gz
```

inside:

```text
data/raw/
```

### 5. Run

```bash
python run_pipeline.py
```

---

## Key Outcomes

- Processed **2.26M+ loan records**
- Built a MySQL **star-schema warehouse**
- Implemented automated data-quality validation
- Implemented financial and status reconciliation
- Achieved **0 reconciliation mismatches**
- Built a reusable, conditionally executed ETL pipeline

---

## Future Improvements

- Apache Spark for larger-scale processing
- Cloud-based storage and orchestration
- Incremental data loading
- Automated monitoring and logging
- CI/CD integration
- Machine learning-based credit-risk prediction
