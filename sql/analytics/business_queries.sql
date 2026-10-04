USE credit_risk_db;


-- ============================================================
-- CREDIT RISK DATA ENGINEERING PROJECT
-- SQL BUSINESS QUESTIONS
-- ============================================================


-- ============================================================
-- PORTFOLIO OVERVIEW
-- ============================================================


-- Q1. What is the total number of loans?

SELECT
    COUNT(*) AS total_loans
FROM fact_loan;


-- ============================================================
-- Q2. What is the total loan amount issued?

SELECT
    ROUND(SUM(loan_amount), 2) AS total_loan_amount
FROM fact_loan;


-- ============================================================
-- Q3. What is the total amount funded?

SELECT
    ROUND(SUM(funded_amount), 2) AS total_funded_amount
FROM fact_loan;


-- ============================================================
-- Q4. What is the average loan amount?

SELECT
    ROUND(AVG(loan_amount), 2) AS average_loan_amount
FROM fact_loan;


-- ============================================================
-- Q5. What is the average interest rate?

SELECT
    ROUND(AVG(interest_rate) * 100, 2) AS average_interest_rate_pct
FROM fact_loan;


-- ============================================================
-- Q6. What is the loan-status distribution?

SELECT
    loan_status,
    COUNT(*) AS loan_count,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM fact_loan),
        2
    ) AS portfolio_percentage
FROM fact_loan
GROUP BY loan_status
ORDER BY loan_count DESC;


-- ============================================================
-- Q7. What is the overall charge-off rate?
-- Definition:
-- Charged Off loans / Total loans
-- ============================================================

SELECT
    COUNT(*) AS total_loans,

    SUM(
        CASE
            WHEN loan_status = 'Charged Off'
            THEN 1
            ELSE 0
        END
    ) AS charged_off_loans,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN loan_status = 'Charged Off'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS charge_off_rate_pct

FROM fact_loan;


-- ============================================================
-- CREDIT RISK
-- ============================================================


-- ============================================================
-- Q8. How does charge-off rate vary by loan grade?
-- ============================================================

SELECT
    l.grade,

    COUNT(*) AS total_loans,

    SUM(
        CASE
            WHEN f.loan_status = 'Charged Off'
            THEN 1
            ELSE 0
        END
    ) AS charged_off_loans,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.loan_status = 'Charged Off'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS charge_off_rate_pct

FROM fact_loan f

JOIN dim_loan l
    ON f.loan_key = l.loan_key

GROUP BY l.grade

ORDER BY l.grade;


-- ============================================================
-- Q9. How does loan volume vary by loan grade?
-- ============================================================

SELECT
    l.grade,
    COUNT(*) AS loan_count,
    ROUND(SUM(f.loan_amount), 2) AS total_loan_amount,
    ROUND(SUM(f.funded_amount), 2) AS total_funded_amount

FROM fact_loan f

JOIN dim_loan l
    ON f.loan_key = l.loan_key

GROUP BY l.grade

ORDER BY loan_count DESC;


-- ============================================================
-- Q10. How does charge-off rate vary by FICO band?
--
-- FICO bands:
-- <580       Poor
-- 580-669    Fair
-- 670-739    Good
-- 740-799    Very Good
-- 800+       Exceptional
-- ============================================================

SELECT

    CASE
        WHEN cp.fico_score < 580 THEN 'Poor'
        WHEN cp.fico_score < 670 THEN 'Fair'
        WHEN cp.fico_score < 740 THEN 'Good'
        WHEN cp.fico_score < 800 THEN 'Very Good'
        ELSE 'Exceptional'
    END AS fico_band,

    COUNT(*) AS total_loans,

    SUM(
        CASE
            WHEN f.loan_status = 'Charged Off'
            THEN 1
            ELSE 0
        END
    ) AS charged_off_loans,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.loan_status = 'Charged Off'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS charge_off_rate_pct

FROM fact_loan f

JOIN dim_credit_profile cp
    ON f.credit_profile_key = cp.credit_profile_key

GROUP BY fico_band

ORDER BY
    CASE fico_band
        WHEN 'Poor' THEN 1
        WHEN 'Fair' THEN 2
        WHEN 'Good' THEN 3
        WHEN 'Very Good' THEN 4
        WHEN 'Exceptional' THEN 5
    END;


-- ============================================================
-- Q11. How does charge-off rate vary by DTI band?
--
-- <10
-- 10-20
-- 20-30
-- 30-40
-- 40+
-- ============================================================

SELECT

    CASE
        WHEN cp.dti < 10 THEN '<10'
        WHEN cp.dti < 20 THEN '10-20'
        WHEN cp.dti < 30 THEN '20-30'
        WHEN cp.dti < 40 THEN '30-40'
        ELSE '40+'
    END AS dti_band,

    COUNT(*) AS total_loans,

    SUM(
        CASE
            WHEN f.loan_status = 'Charged Off'
            THEN 1
            ELSE 0
        END
    ) AS charged_off_loans,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.loan_status = 'Charged Off'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS charge_off_rate_pct

FROM fact_loan f

JOIN dim_credit_profile cp
    ON f.credit_profile_key = cp.credit_profile_key

WHERE cp.dti IS NOT NULL

GROUP BY dti_band

ORDER BY
    CASE dti_band
        WHEN '<10' THEN 1
        WHEN '10-20' THEN 2
        WHEN '20-30' THEN 3
        WHEN '30-40' THEN 4
        WHEN '40+' THEN 5
    END;


-- ============================================================
-- Q12. How does charge-off rate vary by verification status?
-- ============================================================

SELECT

    b.verification_status,

    COUNT(*) AS total_loans,

    SUM(
        CASE
            WHEN f.loan_status = 'Charged Off'
            THEN 1
            ELSE 0
        END
    ) AS charged_off_loans,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.loan_status = 'Charged Off'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS charge_off_rate_pct

FROM fact_loan f

JOIN dim_borrower b
    ON f.borrower_key = b.borrower_key

GROUP BY b.verification_status

ORDER BY charge_off_rate_pct DESC;


-- ============================================================
-- Q13. How does charge-off rate vary by home ownership?
-- ============================================================

SELECT

    b.home_ownership,

    COUNT(*) AS total_loans,

    SUM(
        CASE
            WHEN f.loan_status = 'Charged Off'
            THEN 1
            ELSE 0
        END
    ) AS charged_off_loans,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.loan_status = 'Charged Off'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS charge_off_rate_pct

FROM fact_loan f

JOIN dim_borrower b
    ON f.borrower_key = b.borrower_key

GROUP BY b.home_ownership

ORDER BY charge_off_rate_pct DESC;


-- ============================================================
-- Q14. Which loan purposes have the highest charge-off rates?
-- ============================================================

SELECT

    l.purpose,

    COUNT(*) AS total_loans,

    SUM(
        CASE
            WHEN f.loan_status = 'Charged Off'
            THEN 1
            ELSE 0
        END
    ) AS charged_off_loans,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.loan_status = 'Charged Off'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS charge_off_rate_pct

FROM fact_loan f

JOIN dim_loan l
    ON f.loan_key = l.loan_key

GROUP BY l.purpose

HAVING COUNT(*) >= 100

ORDER BY charge_off_rate_pct DESC;


-- ============================================================
-- LOAN PERFORMANCE
-- ============================================================


-- ============================================================
-- Q15. How much principal has been received?
-- ============================================================

SELECT
    ROUND(SUM(total_principal_received), 2)
        AS total_principal_received
FROM fact_loan;


-- ============================================================
-- Q16. How much interest has been received?
-- ============================================================

SELECT
    ROUND(SUM(total_interest_received), 2)
        AS total_interest_received
FROM fact_loan;


-- ============================================================
-- Q17. How much principal is currently outstanding?
-- ============================================================

SELECT
    ROUND(SUM(outstanding_principal), 2)
        AS total_outstanding_principal
FROM fact_loan;


-- ============================================================
-- Q18. Which loan grades have the highest outstanding principal?
-- ============================================================

SELECT

    l.grade,

    COUNT(*) AS loan_count,

    ROUND(
        SUM(f.outstanding_principal),
        2
    ) AS outstanding_principal

FROM fact_loan f

JOIN dim_loan l
    ON f.loan_key = l.loan_key

GROUP BY l.grade

ORDER BY outstanding_principal DESC;


-- ============================================================
-- GEOGRAPHY & TIME
-- ============================================================


-- ============================================================
-- Q19. Which states have the highest funded amount?
-- ============================================================

SELECT

    g.state_code,

    COUNT(*) AS loan_count,

    ROUND(
        SUM(f.funded_amount),
        2
    ) AS total_funded_amount

FROM fact_loan f

JOIN dim_geography g
    ON f.geography_key = g.geography_key

GROUP BY g.state_code

ORDER BY total_funded_amount DESC;


-- ============================================================
-- Q20. How has loan origination and charge-off rate
-- changed by year?
-- ============================================================

SELECT

    d.year AS issue_year,

    COUNT(*) AS loan_count,

    ROUND(
        SUM(f.loan_amount),
        2
    ) AS total_loan_amount,

    ROUND(
        SUM(f.funded_amount),
        2
    ) AS total_funded_amount,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.loan_status = 'Charged Off'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS charge_off_rate_pct

FROM fact_loan f

JOIN dim_date d
    ON f.issue_date_key = d.date_key

GROUP BY d.year

ORDER BY d.year;