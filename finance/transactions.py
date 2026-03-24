import os
import pandas as pd
from utils.categorization import load_rules, categorize
from utils.paths import TRANSACTIONS_DIR


def load_transactions():
    dfs = []

    if not TRANSACTIONS_DIR.exists():
        return pd.DataFrame()

    for file in os.listdir(TRANSACTIONS_DIR):
        if file.endswith(".csv"):
            path = os.path.join(TRANSACTIONS_DIR, file)
            df = pd.read_csv(path)
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # Normalize RBC format
    df["Transaction Date"] = pd.to_datetime(
        df["Transaction Date"], format="%m/%d/%Y", errors="coerce"
    )

    df = df.dropna(subset=["Transaction Date"])

    df["Month"] = df["Transaction Date"].dt.to_period("M").astype(str)

    df["Description"] = (
        df["Description 1"].fillna("") + " " + df["Description 2"].fillna("")
    )

    df.rename(columns={"CAD$": "Amount"}, inplace=True)

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

    # Categorization
    rules_df = load_rules()
    df["Category"] = df["Description"].apply(lambda x: categorize(x, rules_df))

    return df
