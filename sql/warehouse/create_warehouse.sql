USE credit_risk_db;


-- ============================================================
-- DIMENSION 1: DATE
-- ============================================================

CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20)
);


-- ============================================================
-- DIMENSION 2: LOAN
-- ============================================================

CREATE TABLE dim_loan (
    loan_key INT AUTO_INCREMENT PRIMARY KEY,

    loan_id VARCHAR(30) NOT NULL UNIQUE,

    loan_term_months INT,
    grade VARCHAR(5),
    sub_grade VARCHAR(5),
    purpose VARCHAR(50),
    application_type VARCHAR(30),
    initial_list_status VARCHAR(10)
);


-- ============================================================
-- DIMENSION 3: BORROWER
-- ============================================================

CREATE TABLE dim_borrower (
    borrower_key INT AUTO_INCREMENT PRIMARY KEY,

    loan_id VARCHAR(30) NOT NULL UNIQUE,

    emp_title VARCHAR(255),
    emp_length_years INT,
    home_ownership VARCHAR(20),
    annual_income DECIMAL(15,2),
    verification_status VARCHAR(30)
);


-- ============================================================
-- DIMENSION 4: CREDIT PROFILE
-- ============================================================

CREATE TABLE dim_credit_profile (
    credit_profile_key INT AUTO_INCREMENT PRIMARY KEY,

    loan_id VARCHAR(30) NOT NULL UNIQUE,

    fico_score DECIMAL(6,2),
    dti DECIMAL(10,4),
    delinq_2yrs INT,
    inq_last_6mths INT,
    open_acc INT,
    pub_rec INT,
    revol_bal DECIMAL(15,2),
    revol_util DECIMAL(8,5),
    total_acc INT
);


-- ============================================================
-- DIMENSION 5: GEOGRAPHY
-- ============================================================

CREATE TABLE dim_geography (
    geography_key INT AUTO_INCREMENT PRIMARY KEY,

    state_code VARCHAR(5) NOT NULL UNIQUE
);


-- ============================================================
-- FACT TABLE: LOAN
-- ============================================================

CREATE TABLE fact_loan (
    loan_fact_key BIGINT AUTO_INCREMENT PRIMARY KEY,

    loan_key INT NOT NULL,
    borrower_key INT NOT NULL,
    credit_profile_key INT NOT NULL,
    geography_key INT NOT NULL,
    issue_date_key INT,

    loan_status VARCHAR(50),

    loan_amount DECIMAL(12,2),
    funded_amount DECIMAL(12,2),
    funded_amount_investor DECIMAL(12,2),

    interest_rate DECIMAL(8,5),
    installment DECIMAL(12,2),

    outstanding_principal DECIMAL(15,2),

    total_payment DECIMAL(15,2),
    total_principal_received DECIMAL(15,2),
    total_interest_received DECIMAL(15,2),
    total_late_fees DECIMAL(15,2),

    recoveries DECIMAL(15,2),
    collection_recovery_fee DECIMAL(15,2),

    last_payment_date DATE,
    last_payment_amount DECIMAL(15,2),

    FOREIGN KEY (loan_key)
        REFERENCES dim_loan(loan_key),

    FOREIGN KEY (borrower_key)
        REFERENCES dim_borrower(borrower_key),

    FOREIGN KEY (credit_profile_key)
        REFERENCES dim_credit_profile(credit_profile_key),

    FOREIGN KEY (geography_key)
        REFERENCES dim_geography(geography_key),

    FOREIGN KEY (issue_date_key)
        REFERENCES dim_date(date_key)
);