# Data Dictionary

## Fact Loan

### loan_fact_key

Surrogate key for the loan fact record.

### loan_key

Foreign key referencing `dim_loan`.

### borrower_key

Foreign key referencing `dim_borrower`.

### credit_profile_key

Foreign key referencing `dim_credit_profile`.

### geography_key

Foreign key referencing `dim_geography`.

### issue_date_key

Foreign key referencing `dim_date`.

### loan_status

Current recorded loan status.

### loan_amount

Original requested loan amount.

### funded_amount

Amount funded for the loan.

### funded_amount_investor

Amount funded by investors.

### interest_rate

Interest rate associated with the loan.

### installment

Scheduled monthly installment.

### outstanding_principal

Remaining principal amount.

### total_payment

Total payment received.

### total_principal_received

Total principal received.

### total_interest_received

Total interest received.

### recoveries

Amount recovered after charge-off.

## Dimensions

### dim_loan

Contains loan classification and product information.

### dim_borrower

Contains borrower employment, income and ownership information.

### dim_credit_profile

Contains borrower credit characteristics.

### dim_geography

Contains borrower state information.

### dim_date

Provides calendar attributes for time-based analysis.