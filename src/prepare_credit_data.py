from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "uci_credit_default_raw.csv"
)

PROCESSED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "credit_default_processed.csv"
)


credit_df = pd.read_csv(RAW_FILE)


COLUMN_MAPPING = {
    "ID": "customer_id",
    "X1": "credit_limit",
    "X2": "sex_code",
    "X3": "education_code",
    "X4": "marital_status_code",
    "X5": "age",

    "X6": "repayment_status_sep",
    "X7": "repayment_status_aug",
    "X8": "repayment_status_jul",
    "X9": "repayment_status_jun",
    "X10": "repayment_status_may",
    "X11": "repayment_status_apr",

    "X12": "bill_amount_sep",
    "X13": "bill_amount_aug",
    "X14": "bill_amount_jul",
    "X15": "bill_amount_jun",
    "X16": "bill_amount_may",
    "X17": "bill_amount_apr",

    "X18": "payment_amount_sep",
    "X19": "payment_amount_aug",
    "X20": "payment_amount_jul",
    "X21": "payment_amount_jun",
    "X22": "payment_amount_may",
    "X23": "payment_amount_apr",
}


credit_df = credit_df.rename(
    columns=COLUMN_MAPPING
)


# Add readable demographic labels while keeping
# the original numeric codes.

credit_df["sex"] = (
    credit_df["sex_code"]
    .map({
        1: "Male",
        2: "Female",
    })
    .fillna("Unknown")
)


credit_df["education"] = (
    credit_df["education_code"]
    .map({
        1: "Graduate School",
        2: "University",
        3: "High School",
        4: "Other",
    })
    .fillna("Unknown / Other")
)


credit_df["marital_status"] = (
    credit_df["marital_status_code"]
    .map({
        1: "Married",
        2: "Single",
        3: "Other",
    })
    .fillna("Unknown")
)


# Reorder key business fields near the front.

front_columns = [
    "customer_id",
    "credit_limit",
    "sex",
    "education",
    "marital_status",
    "age",
    "default_next_month",
]

remaining_columns = [
    column
    for column in credit_df.columns
    if column not in front_columns
]

credit_df = credit_df[
    front_columns + remaining_columns
]


credit_df.to_csv(
    PROCESSED_FILE,
    index=False,
)


print(
    "Processed credit-risk dataset created successfully."
)

print(
    f"Rows: {credit_df.shape[0]:,}"
)

print(
    f"Columns: {credit_df.shape[1]}"
)

print(
    f"Default rate: "
    f"{credit_df['default_next_month'].mean():.2%}"
)

print(
    f"\nSaved to:\n{PROCESSED_FILE}"
)