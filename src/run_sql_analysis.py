from pathlib import Path

import duckdb
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PORTFOLIO_FILE = (
    PROCESSED_DIR
    / "credit_default_processed.csv"
)

SCORED_FILE = (
    PROCESSED_DIR
    / "credit_risk_scored_test.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "sql_outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Create DuckDB connection
# ---------------------------------------------------------

connection = duckdb.connect()


# ---------------------------------------------------------
# Load portfolio datasets as DuckDB views
# ---------------------------------------------------------

connection.execute(
    f"""
    CREATE OR REPLACE VIEW credit_portfolio AS
    SELECT *
    FROM read_csv_auto(
        '{PORTFOLIO_FILE.as_posix()}'
    )
    """
)

connection.execute(
    f"""
    CREATE OR REPLACE VIEW scored_portfolio AS
    SELECT *
    FROM read_csv_auto(
        '{SCORED_FILE.as_posix()}'
    )
    """
)


# ---------------------------------------------------------
# 1. Overall portfolio summary
# ---------------------------------------------------------

overall_summary_query = """
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

FROM credit_portfolio
"""

overall_summary = connection.execute(
    overall_summary_query
).df()

overall_summary.to_csv(
    OUTPUT_DIR / "overall_portfolio_summary.csv",
    index=False,
)


# ---------------------------------------------------------
# 2. Credit limit segmentation
# ---------------------------------------------------------

credit_limit_query = """
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
    MIN(credit_limit)
"""

credit_limit_summary = connection.execute(
    credit_limit_query
).df()

credit_limit_summary.to_csv(
    OUTPUT_DIR / "credit_limit_risk_summary.csv",
    index=False,
)


# ---------------------------------------------------------
# 3. Recent repayment behavior
# ---------------------------------------------------------

repayment_query = """
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

ORDER BY repayment_status_sep
"""

repayment_summary = connection.execute(
    repayment_query
).df()

repayment_summary.to_csv(
    OUTPUT_DIR / "repayment_status_summary.csv",
    index=False,
)


# ---------------------------------------------------------
# 4. Model risk-band performance
# ---------------------------------------------------------

risk_band_query = """
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
    END
"""

risk_band_summary = connection.execute(
    risk_band_query
).df()

risk_band_summary.to_csv(
    OUTPUT_DIR / "risk_band_summary.csv",
    index=False,
)


# ---------------------------------------------------------
# 5. High-risk concentration
# ---------------------------------------------------------

high_risk_query = """
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
)
"""

high_risk_summary = connection.execute(
    high_risk_query
).df()

high_risk_summary.to_csv(
    OUTPUT_DIR / "high_risk_concentration.csv",
    index=False,
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print("\nCREDIT RISK SQL ANALYSIS")
print("=" * 70)

print("\nOverall Portfolio Summary")
print(overall_summary.to_string(index=False))

print("\nCredit Limit Risk Summary")
print(credit_limit_summary.to_string(index=False))

print("\nRisk Band Summary")
print(risk_band_summary.to_string(index=False))

print("\nHigh-Risk Concentration")
print(high_risk_summary.to_string(index=False))

print(
    f"\nSQL analysis outputs saved to:\n{OUTPUT_DIR}"
)

connection.close()