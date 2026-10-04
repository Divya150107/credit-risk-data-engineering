# Data Quality Documentation

## Initial Data Profile

Raw dataset:

- Rows: 2,260,701
- Columns: 151
- Duplicate rows: 0
- Duplicate loan IDs: 0

## Data Quality Issues Identified

The following issues were identified during profiling:

- Completely empty columns
- Missing loan information
- Non-positive annual income
- Invalid DTI values
- DTI special value of 999
- Revolving utilization values above 100
- Missing categorical and numerical values
- Non-standard loan-status descriptions

## Cleaning Results

After column selection and cleaning:

- Final rows: 2,260,668
- Final columns: 40
- Rows removed: 33
- Duplicate loan IDs: 0
- Missing loan IDs: 0
- Invalid annual income values: 0
- Invalid DTI values: 0
- Invalid revolving utilization values: 0

## Warehouse Validation

The following validations were performed:

1. Staging-to-fact row count
2. Duplicate fact records
3. Orphan loan keys
4. Orphan borrower keys
5. Orphan credit-profile keys
6. Orphan geography keys
7. Orphan date keys
8. Loan amount reconciliation
9. Funded amount reconciliation
10. Investor funded amount reconciliation
11. Total payment reconciliation
12. Principal received reconciliation
13. Interest received reconciliation
14. Recoveries reconciliation
15. Loan-level amount reconciliation
16. Loan-status reconciliation

All completed reconciliation checks returned zero mismatches.