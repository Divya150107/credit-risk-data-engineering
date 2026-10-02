CREATE OR REPLACE VIEW vw_loan_analytics AS

SELECT
    -- Loan identifiers
    f.loan_fact_key,
    l.loan_id,

    -- Date information
    d.full_date AS issue_date,
    d.year AS issue_year,
    d.quarter AS issue_quarter,
    d.month AS issue_month,
    d.month_name AS issue_month_name,

    -- Loan characteristics
    l.loan_term_months,
    l.grade,
    l.sub_grade,
    l.purpose,
    l.application_type,
    l.initial_list_status,

    -- Borrower information
    b.emp_title,
    b.emp_length_years,
    b.home_ownership,
    b.annual_income,
    b.verification_status,

    -- Credit profile
    cp.fico_score,
    cp.dti,
    cp.delinq_2yrs,
    cp.inq_last_6mths,
    cp.open_acc,
    cp.pub_rec,
    cp.revol_bal,
    cp.revol_util,
    cp.total_acc,

    -- Geography
    g.state_code,

    -- Loan status
    f.loan_status,

    -- Financial measures
    f.loan_amount,
    f.funded_amount,
    f.funded_amount_investor,
    f.interest_rate,
    f.installment,
    f.outstanding_principal,
    f.total_payment,
    f.total_principal_received,
    f.total_interest_received,
    f.total_late_fees,
    f.recoveries,
    f.collection_recovery_fee,
    f.last_payment_date,
    f.last_payment_amount

FROM fact_loan f

LEFT JOIN dim_loan l
    ON f.loan_key = l.loan_key

LEFT JOIN dim_borrower b
    ON f.borrower_key = b.borrower_key

LEFT JOIN dim_credit_profile cp
    ON f.credit_profile_key = cp.credit_profile_key

LEFT JOIN dim_geography g
    ON f.geography_key = g.geography_key

LEFT JOIN dim_date d
    ON f.issue_date_key = d.date_key;