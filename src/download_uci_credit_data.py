from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Download public UCI dataset
# Dataset ID 350:
# Default of Credit Card Clients
# ---------------------------------------------------------

dataset = fetch_ucirepo(id=350)

features = dataset.data.features.copy()
target = dataset.data.targets.copy()
ids = dataset.data.ids


# ---------------------------------------------------------
# Combine ID, features, and target
# ---------------------------------------------------------

frames = []

if ids is not None:
    frames.append(ids.copy())

frames.append(features)
frames.append(target)

credit_df = pd.concat(
    frames,
    axis=1,
)


# Give the target a clear business-friendly name
original_target_name = target.columns[0]

credit_df = credit_df.rename(
    columns={
        original_target_name: "default_next_month"
    }
)


# ---------------------------------------------------------
# Save raw dataset
# ---------------------------------------------------------

data_file = (
    RAW_DATA_DIR
    / "uci_credit_default_raw.csv"
)

credit_df.to_csv(
    data_file,
    index=False,
)


# ---------------------------------------------------------
# Save UCI variable dictionary
# ---------------------------------------------------------

dictionary_file = (
    RAW_DATA_DIR
    / "uci_variable_dictionary.csv"
)

dataset.variables.to_csv(
    dictionary_file,
    index=False,
)


# ---------------------------------------------------------
# Verification output
# ---------------------------------------------------------

print(
    "UCI credit-default dataset downloaded successfully."
)

print(
    f"Rows: {credit_df.shape[0]:,}"
)

print(
    f"Columns: {credit_df.shape[1]}"
)

print(
    f"Default records: "
    f"{credit_df['default_next_month'].sum():,}"
)

print(
    f"Default rate: "
    f"{credit_df['default_next_month'].mean():.2%}"
)

print(
    f"\nDataset saved to:\n{data_file}"
)

print(
    f"\nVariable dictionary saved to:\n"
    f"{dictionary_file}"
)