from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "credit_default_processed.csv"
)

SCORED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "credit_risk_scored_test.csv"
)


processed_df = pd.read_csv(PROCESSED_FILE)
scored_df = pd.read_csv(SCORED_FILE)


def test_processed_portfolio_record_count():
    assert len(processed_df) == 30000


def test_scored_test_record_count():
    assert len(scored_df) == 6000


def test_portfolio_default_rate():
    default_rate = processed_df["default_next_month"].mean()

    assert round(default_rate * 100, 2) == 22.12


def test_scored_customer_ids_are_unique():
    assert scored_df["customer_id"].is_unique


def test_risk_scores_are_valid_probabilities():
    assert scored_df["default_risk_score"].between(
        0,
        1,
    ).all()


def test_risk_bands_are_valid():
    valid_bands = {
        "Low",
        "Moderate",
        "Elevated",
        "High",
        "Very High",
    }

    actual_bands = set(
        scored_df["risk_band"].dropna().unique()
    )

    assert actual_bands.issubset(valid_bands)


def test_key_scoring_fields_have_no_missing_values():
    key_columns = [
        "customer_id",
        "actual_default",
        "default_risk_score",
        "risk_band",
    ]

    assert (
        scored_df[key_columns]
        .isna()
        .sum()
        .sum()
        == 0
    )


def test_risk_bands_show_increasing_default_risk():
    band_order = [
        "Low",
        "Moderate",
        "Elevated",
        "High",
        "Very High",
    ]

    band_summary = (
        scored_df
        .groupby("risk_band")["actual_default"]
        .mean()
        .reindex(band_order)
    )

    assert band_summary.is_monotonic_increasing


def test_high_risk_population_exists():
    high_risk_df = scored_df[
        scored_df["risk_band"].isin(
            [
                "High",
                "Very High",
            ]
        )
    ]

    assert len(high_risk_df) > 0


def test_high_risk_population_has_elevated_default_rate():
    high_risk_df = scored_df[
        scored_df["risk_band"].isin(
            [
                "High",
                "Very High",
            ]
        )
    ]

    observed_default_rate = (
        high_risk_df["actual_default"].mean()
    )

    assert observed_default_rate > 0.50