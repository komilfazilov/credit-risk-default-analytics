-- ============================================================
-- Credit Risk & Default Analytics
-- SQL Portfolio Analysis Layer
-- Engine: DuckDB
-- ============================================================


-- ------------------------------------------------------------
-- 1. Load processed portfolio data
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW credit_portfolio AS
SELECT *
FROM read_csv_auto(
    'data/processed/credit_default_processed.csv'
);


-- ------------------------------------------------------------
-- 2. Load scored test population
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW scored_portfolio AS
SELECT *
FROM read_csv_auto(
    'data/processed/credit_risk_scored_test.csv'
);


-- ------------------------------------------------------------
-- 3. Overall portfolio summary
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_clients,

    SUM(default_next_month) AS default_clients,

    ROUND(
        AVG(default_next_month) * 100,
        2
    ) AS default_rate_pct,

    ROUND(
        AVG(credit_limit),
        2
    ) AS average_credit_limit

FROM credit_portfolio;


-- ------------------------------------------------------------
-- 4. Default rate by credit-limit band
-- ------------------------------------------------------------

SELECT
    CASE
        WHEN credit_limit < 50000
            THEN 'Under 50K'

        WHEN credit_limit < 100000
            THEN '50K-99K'

        WHEN credit_limit < 200000
            THEN '100K-199K'

        WHEN credit_limit < 300000
            THEN '200K-299K'

        WHEN credit_limit < 500000
            THEN '300K-499K'

        ELSE '500K+'
    END AS credit_limit_band,

    COUNT(*) AS clients,

    SUM(default_next_month) AS defaults,

    ROUND(
        AVG(default_next_month) * 100,
        2
    ) AS default_rate_pct

FROM credit_portfolio

GROUP BY 1

ORDER BY
    MIN(credit_limit);


-- ------------------------------------------------------------
-- 5. Recent repayment behavior
-- ------------------------------------------------------------

SELECT
    repayment_status_sep,

    COUNT(*) AS clients,

    SUM(default_next_month) AS defaults,

    ROUND(
        AVG(default_next_month) * 100,
        2
    ) AS default_rate_pct

FROM credit_portfolio

GROUP BY repayment_status_sep

ORDER BY repayment_status_sep;


-- ------------------------------------------------------------
-- 6. Model risk-band performance
-- ------------------------------------------------------------

SELECT
    risk_band,

    COUNT(*) AS clients,

    SUM(actual_default) AS actual_defaults,

    ROUND(
        AVG(actual_default) * 100,
        2
    ) AS observed_default_rate_pct,

    ROUND(
        AVG(default_risk_score) * 100,
        2
    ) AS average_model_score_pct

FROM scored_portfolio

GROUP BY risk_band

ORDER BY
    CASE risk_band
        WHEN 'Low' THEN 1
        WHEN 'Moderate' THEN 2
        WHEN 'Elevated' THEN 3
        WHEN 'High' THEN 4
        WHEN 'Very High' THEN 5
        ELSE 6
    END;


-- ------------------------------------------------------------
-- 7. High-risk portfolio concentration
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS high_risk_clients,

    ROUND(
        COUNT(*) * 100.0
        / (
            SELECT COUNT(*)
            FROM scored_portfolio
        ),
        2
    ) AS pct_of_scored_population,

    ROUND(
        AVG(default_risk_score) * 100,
        2
    ) AS average_risk_score_pct,

    ROUND(
        AVG(actual_default) * 100,
        2
    ) AS observed_default_rate_pct,

    ROUND(
        SUM(credit_limit),
        2
    ) AS total_credit_limit

FROM scored_portfolio

WHERE risk_band IN (
    'High',
    'Very High'
);