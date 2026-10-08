from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="Credit Risk & Default Analytics",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

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

MODEL_COMPARISON_FILE = (
    PROJECT_ROOT
    / "reports"
    / "model_comparison.csv"
)

FEATURE_IMPORTANCE_FILE = (
    PROJECT_ROOT
    / "reports"
    / "feature_importance.csv"
)


# ============================================================
# Reference mappings
# ============================================================

RISK_ORDER = [
    "Low",
    "Moderate",
    "Elevated",
    "High",
    "Very High",
]

REPAYMENT_STATUS_LABELS = {
    -2: "No Consumption",
    -1: "Paid in Full",
    0: "Revolving / Current",
    1: "1 Month Delay",
    2: "2 Months Delay",
    3: "3 Months Delay",
    4: "4 Months Delay",
    5: "5 Months Delay",
    6: "6 Months Delay",
    7: "7 Months Delay",
    8: "8 Months Delay",
}


# ============================================================
# Load data
# ============================================================

@st.cache_data
def load_data():

    portfolio_df = pd.read_csv(
        PROCESSED_FILE
    )

    scored_df = pd.read_csv(
        SCORED_FILE
    )

    model_df = pd.read_csv(
        MODEL_COMPARISON_FILE
    )

    importance_df = pd.read_csv(
        FEATURE_IMPORTANCE_FILE
    )

    return (
        portfolio_df,
        scored_df,
        model_df,
        importance_df,
    )


(
    portfolio_df,
    scored_df,
    model_df,
    importance_df,
) = load_data()


# ============================================================
# Header
# ============================================================

st.title(
    "Credit Risk & Default Analytics Dashboard"
)

st.caption(
    "Portfolio analytics and predictive-risk demonstration "
    "using the UCI Default of Credit Card Clients dataset."
)

st.info(
    "This project is intended for educational and portfolio "
    "demonstration purposes. Model scores are not production "
    "probability-of-default estimates and have not undergone "
    "formal model validation, calibration, regulatory approval, "
    "or production governance."
)


# ============================================================
# Executive metrics
# ============================================================

portfolio_clients = len(
    portfolio_df
)

portfolio_default_rate = (
    portfolio_df[
        "default_next_month"
    ].mean()
)

scored_clients = len(
    scored_df
)

high_risk_df = scored_df[
    scored_df[
        "risk_band"
    ].isin(
        [
            "High",
            "Very High",
        ]
    )
]

high_risk_pct = (
    len(high_risk_df)
    / len(scored_df)
)

high_risk_default_rate = (
    high_risk_df[
        "actual_default"
    ].mean()
)


metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = (
    st.columns(5)
)

metric_col1.metric(
    "Portfolio Clients",
    f"{portfolio_clients:,}",
)

metric_col2.metric(
    "Portfolio Default Rate",
    f"{portfolio_default_rate:.2%}",
)

metric_col3.metric(
    "Scored Test Population",
    f"{scored_clients:,}",
)

metric_col4.metric(
    "High / Very High Risk",
    f"{high_risk_pct:.2%}",
)

metric_col5.metric(
    "High-Risk Observed Default",
    f"{high_risk_default_rate:.2%}",
)


# ============================================================
# Tabs
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Portfolio Overview",
        "Risk Segmentation",
        "Model Performance",
        "Data Explorer",
    ]
)


# ============================================================
# TAB 1 — Portfolio Overview
# ============================================================

with tab1:

    st.header(
        "Portfolio Risk Overview"
    )

    # --------------------------------------------------------
    # Credit-limit analysis
    # --------------------------------------------------------

    credit_limit_df = (
        portfolio_df.copy()
    )

    credit_limit_df[
        "credit_limit_band"
    ] = pd.cut(
        credit_limit_df[
            "credit_limit"
        ],
        bins=[
            0,
            50000,
            100000,
            200000,
            300000,
            500000,
            float("inf"),
        ],
        labels=[
            "Under 50K",
            "50K–99K",
            "100K–199K",
            "200K–299K",
            "300K–499K",
            "500K+",
        ],
        right=False,
    )

    credit_limit_summary = (
        credit_limit_df
        .groupby(
            "credit_limit_band",
            observed=True,
        )
        .agg(
            clients=(
                "customer_id",
                "count",
            ),
            defaults=(
                "default_next_month",
                "sum",
            ),
            default_rate=(
                "default_next_month",
                "mean",
            ),
        )
        .reset_index()
    )

    credit_limit_summary[
        "default_rate_pct"
    ] = (
        credit_limit_summary[
            "default_rate"
        ]
        * 100
    )


    chart_col1, chart_col2 = (
        st.columns(2)
    )


    with chart_col1:

        fig = px.bar(
            credit_limit_summary,
            x="credit_limit_band",
            y="default_rate_pct",
            text="default_rate_pct",
            title=(
                "Default Rate by Credit Limit Band"
            ),
            labels={
                "credit_limit_band":
                    "Credit Limit Band",
                "default_rate_pct":
                    "Default Rate (%)",
            },
        )

        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )


    # --------------------------------------------------------
    # Recent repayment-status analysis
    # --------------------------------------------------------

    repayment_summary = (
        portfolio_df
        .groupby(
            "repayment_status_sep"
        )
        .agg(
            clients=(
                "customer_id",
                "count",
            ),
            default_rate=(
                "default_next_month",
                "mean",
            ),
        )
        .reset_index()
        .sort_values(
            "repayment_status_sep"
        )
    )

    repayment_summary[
        "default_rate_pct"
    ] = (
        repayment_summary[
            "default_rate"
        ]
        * 100
    )

    repayment_summary[
        "repayment_status_label"
    ] = (
        repayment_summary[
            "repayment_status_sep"
        ]
        .map(
            REPAYMENT_STATUS_LABELS
        )
    )


    with chart_col2:

        fig = px.bar(
            repayment_summary,
            x="repayment_status_label",
            y="default_rate_pct",
            text="default_rate_pct",
            title=(
                "Default Rate by Recent Repayment Status"
            ),
            labels={
                "repayment_status_label":
                    "Recent Repayment Status",
                "default_rate_pct":
                    "Default Rate (%)",
            },
        )

        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )

        fig.update_layout(
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )


    st.subheader(
        "Portfolio Interpretation"
    )

    st.markdown(
        """
- Lower credit-limit segments exhibit materially higher historical default rates.
- Recent repayment behavior shows strong differentiation between lower- and higher-risk clients.
- Behavioral repayment information appears more informative than simple demographic segmentation.
        """
    )


# ============================================================
# TAB 2 — Risk Segmentation
# ============================================================

with tab2:

    st.header(
        "Model Risk Segmentation"
    )

    risk_summary = (
        scored_df
        .groupby(
            "risk_band",
            observed=True,
        )
        .agg(
            clients=(
                "customer_id",
                "count",
            ),
            actual_defaults=(
                "actual_default",
                "sum",
            ),
            observed_default_rate=(
                "actual_default",
                "mean",
            ),
            average_model_score=(
                "default_risk_score",
                "mean",
            ),
            total_credit_limit=(
                "credit_limit",
                "sum",
            ),
        )
        .reset_index()
    )

    risk_summary[
        "risk_band"
    ] = pd.Categorical(
        risk_summary[
            "risk_band"
        ],
        categories=RISK_ORDER,
        ordered=True,
    )

    risk_summary = (
        risk_summary
        .sort_values(
            "risk_band"
        )
    )

    risk_summary[
        "observed_default_rate_pct"
    ] = (
        risk_summary[
            "observed_default_rate"
        ]
        * 100
    )

    risk_summary[
        "average_model_score_pct"
    ] = (
        risk_summary[
            "average_model_score"
        ]
        * 100
    )


    risk_chart_col1, risk_chart_col2 = (
        st.columns(2)
    )


    with risk_chart_col1:

        fig = px.bar(
            risk_summary,
            x="risk_band",
            y="observed_default_rate_pct",
            text="observed_default_rate_pct",
            title=(
                "Observed Default Rate by Risk Band"
            ),
            labels={
                "risk_band":
                    "Model Risk Band",
                "observed_default_rate_pct":
                    "Observed Default Rate (%)",
            },
        )

        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )


    with risk_chart_col2:

        fig = px.bar(
            risk_summary,
            x="risk_band",
            y="clients",
            text="clients",
            title=(
                "Scored Population by Risk Band"
            ),
            labels={
                "risk_band":
                    "Model Risk Band",
                "clients":
                    "Clients",
            },
        )

        fig.update_traces(
            textposition="outside",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )


    st.subheader(
        "Risk Band Summary"
    )

    display_risk_summary = (
        risk_summary[
            [
                "risk_band",
                "clients",
                "actual_defaults",
                "observed_default_rate_pct",
                "average_model_score_pct",
                "total_credit_limit",
            ]
        ]
        .copy()
    )

    display_risk_summary[
        "observed_default_rate_pct"
    ] = (
        display_risk_summary[
            "observed_default_rate_pct"
        ]
        .map(
            lambda x: f"{x:.2f}%"
        )
    )

    display_risk_summary[
        "average_model_score_pct"
    ] = (
        display_risk_summary[
            "average_model_score_pct"
        ]
        .map(
            lambda x: f"{x:.2f}%"
        )
    )

    display_risk_summary[
        "total_credit_limit"
    ] = (
        display_risk_summary[
            "total_credit_limit"
        ]
        .map(
            lambda x: f"${x:,.0f}"
        )
    )

    display_risk_summary = (
        display_risk_summary.rename(
            columns={
                "risk_band":
                    "Risk Band",
                "clients":
                    "Clients",
                "actual_defaults":
                    "Actual Defaults",
                "observed_default_rate_pct":
                    "Observed Default Rate",
                "average_model_score_pct":
                    "Average Model Score",
                "total_credit_limit":
                    "Total Credit Limit",
            }
        )
    )

    st.dataframe(
        display_risk_summary,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# TAB 3 — Model Performance
# ============================================================

with tab3:

    st.header(
        "Model Performance & Interpretation"
    )

    st.subheader(
        "Model Comparison"
    )

    display_model_df = (
        model_df.copy()
    )

    percentage_columns = [
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "ROC-AUC",
    ]

    for column in percentage_columns:

        display_model_df[
            column
        ] = (
            display_model_df[
                column
            ]
            .map(
                lambda x: f"{x:.2%}"
            )
        )

    st.dataframe(
        display_model_df,
        width="stretch",
        hide_index=True,
    )


    # --------------------------------------------------------
    # Model comparison chart
    # --------------------------------------------------------

    model_long = model_df.melt(
        id_vars="Model",
        value_vars=[
            "Precision",
            "Recall",
            "F1 Score",
            "ROC-AUC",
        ],
        var_name="Metric",
        value_name="Score",
    )

    fig = px.bar(
        model_long,
        x="Metric",
        y="Score",
        color="Model",
        barmode="group",
        title=(
            "Model Performance Comparison"
        ),
        labels={
            "Score":
                "Model Performance Score",
        },
    )

    fig.update_layout(
        yaxis_tickformat=".0%"
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )


    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    st.subheader(
        "Top Predictive Features"
    )

    top_features = (
        importance_df
        .head(10)
        .copy()
    )

    fig = px.bar(
        top_features,
        x="Importance",
        y="Feature",
        orientation="h",
        title=(
            "Top 10 Random Forest Feature Importances"
        ),
        labels={
            "Importance":
                "Feature Importance",
            "Feature":
                "Risk Feature",
        },
    )

    fig.update_layout(
        yaxis={
            "categoryorder":
                "total ascending"
        }
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )


    st.markdown(
        """
**Interpretation:** Recent repayment-status variables are the strongest predictive contributors in the Random Forest model.

Credit limit and recent billing/payment behavior also contribute to risk differentiation.

Feature importance measures predictive contribution rather than causality or direction of effect.
        """
    )


# ============================================================
# TAB 4 — Data Explorer
# ============================================================

with tab4:

    st.header(
        "Scored Portfolio Explorer"
    )

    selected_risk_bands = (
        st.multiselect(
            "Risk Band",
            options=RISK_ORDER,
            default=RISK_ORDER,
        )
    )

    filtered_df = (
        scored_df[
            scored_df[
                "risk_band"
            ].isin(
                selected_risk_bands
            )
        ]
        .copy()
    )

    st.write(
        f"Displaying {len(filtered_df):,} scored records"
    )


    explorer_df = (
        filtered_df[
            [
                "customer_id",
                "credit_limit",
                "repayment_status_sep",
                "bill_amount_sep",
                "payment_amount_sep",
                "actual_default",
                "default_risk_score",
                "risk_band",
            ]
        ]
        .copy()
    )


    # Human-readable repayment status
    explorer_df[
        "repayment_status_sep"
    ] = (
        explorer_df[
            "repayment_status_sep"
        ]
        .map(
            REPAYMENT_STATUS_LABELS
        )
    )


    # Convert risk score to percentage
    explorer_df[
        "default_risk_score"
    ] = (
        explorer_df[
            "default_risk_score"
        ]
        * 100
    )


    explorer_df = (
        explorer_df.rename(
            columns={
                "customer_id":
                    "Customer ID",
                "credit_limit":
                    "Credit Limit",
                "repayment_status_sep":
                    "Recent Repayment Status",
                "bill_amount_sep":
                    "Recent Bill Amount",
                "payment_amount_sep":
                    "Recent Payment Amount",
                "actual_default":
                    "Actual Default",
                "default_risk_score":
                    "Model Risk Score",
                "risk_band":
                    "Risk Band",
            }
        )
    )


    st.dataframe(
        explorer_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Credit Limit":
                st.column_config.NumberColumn(
                    "Credit Limit",
                    format="$%d",
                ),
            "Recent Bill Amount":
                st.column_config.NumberColumn(
                    "Recent Bill Amount",
                    format="$%d",
                ),
            "Recent Payment Amount":
                st.column_config.NumberColumn(
                    "Recent Payment Amount",
                    format="$%d",
                ),
            "Model Risk Score":
                st.column_config.NumberColumn(
                    "Model Risk Score",
                    format="%.2f%%",
                ),
        },
    )