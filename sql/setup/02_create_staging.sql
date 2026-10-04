-- ============================================================
-- CREDIT RISK DATA ENGINEERING PROJECT
-- STAGING TABLE SETUP
-- ============================================================

USE credit_risk_db;


-- ============================================================
-- STAGING TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS staging_loan_data (

    id VARCHAR(30) PRIMARY KEY,

    loan_amnt DECIMAL(12,2),

    funded_amnt DECIMAL(12,2),

    funded_amnt_inv DECIMAL(12,2),

    term INT,

    int_rate DECIMAL(8,5),

    installment DECIMAL(12,2),

    grade VARCHAR(5),

    sub_grade VARCHAR(5),

    emp_title VARCHAR(255),

    emp_length INT,

    home_ownership VARCHAR(20),

    annual_inc DECIMAL(15,2),

    verification_status VARCHAR(30),

    addr_state VARCHAR(5),

    dti DECIMAL(10,4),

    delinq_2yrs INT,

    fico_range_low INT,

    fico_range_high INT,

    inq_last_6mths INT,

    open_acc INT,

    pub_rec INT,

    revol_bal DECIMAL(15,2),

    revol_util DECIMAL(8,5),

    total_acc INT,

    issue_d DATE,

    loan_status VARCHAR(50),

    purpose VARCHAR(50),

    application_type VARCHAR(30),

    initial_list_status VARCHAR(10),

    out_prncp DECIMAL(15,2),

    total_pymnt DECIMAL(15,2),

    total_rec_prncp DECIMAL(15,2),

    total_rec_int DECIMAL(15,2),

    total_rec_late_fee DECIMAL(15,2),

    recoveries DECIMAL(15,2),

    collection_recovery_fee DECIMAL(15,2),

    last_pymnt_d DATE,

    last_pymnt_amnt DECIMAL(15,2),

    fico_score DECIMAL(6,2)

);