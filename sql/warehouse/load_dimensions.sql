USE credit_risk_db;


-- ============================================================
-- 1. LOAD DATE DIMENSION
-- ============================================================

INSERT INTO dim_date (
    date_key,
    full_date,
    year,
    quarter,
    month,
    month_name
)
SELECT DISTINCT
    YEAR(issue_d) * 10000
        + MONTH(issue_d) * 100
        + DAY(issue_d) AS date_key,

    issue_d AS full_date,

    YEAR(issue_d) AS year,

    QUARTER(issue_d) AS quarter,

    MONTH(issue_d) AS month,

    MONTHNAME(issue_d) AS month_name

FROM staging_loan_data
WHERE issue_d IS NOT NULL;


-- ============================================================
-- 2. LOAD LOAN DIMENSION
-- ============================================================

INSERT INTO dim_loan (
    loan_id,
    loan_term_months,
    grade,
    sub_grade,
    purpose,
    application_type,
    initial_list_status
)
SELECT
    id,
    term,
    grade,
    sub_grade,
    purpose,
    application_type,
    initial_list_status

FROM staging_loan_data;


-- ============================================================
-- 3. LOAD BORROWER DIMENSION
-- ============================================================

INSERT INTO dim_borrower (
    loan_id,
    emp_title,
    emp_length_years,
    home_ownership,
    annual_income,
    verification_status
)
SELECT
    id,
    emp_title,
    emp_length,
    home_ownership,
    annual_inc,
    verification_status

FROM staging_loan_data;


-- ============================================================
-- 4. LOAD CREDIT PROFILE DIMENSION
-- ============================================================

INSERT INTO dim_credit_profile (
    loan_id,
    fico_score,
    dti,
    delinq_2yrs,
    inq_last_6mths,
    open_acc,
    pub_rec,
    revol_bal,
    revol_util,
    total_acc
)
SELECT
    id,
    fico_score,
    dti,
    delinq_2yrs,
    inq_last_6mths,
    open_acc,
    pub_rec,
    revol_bal,
    revol_util,
    total_acc

FROM staging_loan_data;


-- ============================================================
-- 5. LOAD GEOGRAPHY DIMENSION
-- ============================================================

INSERT INTO dim_geography (
    state_code
)
SELECT DISTINCT
    addr_state

FROM staging_loan_data

WHERE addr_state IS NOT NULL;