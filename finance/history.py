import pandas as pd
from utils.paths import BALANCES_HISTORY_FILE


def build_net_worth_history():
    df = load_balances_history()

    if df.empty:
        return pd.DataFrame(columns=["date", "net_worth", "credit_utilization"])

    # Ensure correct types
    df["date"] = pd.to_datetime(df["date"])

    history = []

    for date, group in df.groupby("date"):
        assets = group[group["type"] == "Asset"]["balance"].sum()
        liabilities = group[group["type"] == "Liability"]["balance"].sum()

        net_worth = assets - liabilities

        # Credit utilization
        credit = group[group["account"] == "Credit Card"]
        if not credit.empty and credit["limit"].iloc[0] > 0:
            utilization = (credit["balance"].iloc[0] / credit["limit"].iloc[0]) * 100
        else:
            utilization = 0

        history.append(
            {
                "date": date,
                "net_worth": net_worth,
                "credit_utilization": utilization,
            }
        )

    history_df = pd.DataFrame(history).sort_values("date")

    return history_df


def load_balances_history():
    if BALANCES_HISTORY_FILE.exists():
        df = pd.read_csv(BALANCES_HISTORY_FILE)

        df["balance"] = pd.to_numeric(df["balance"], errors="coerce").fillna(0)
        df["limit"] = pd.to_numeric(df["limit"], errors="coerce").fillna(0)

        return df

    return pd.DataFrame(columns=["date", "account", "type", "balance", "limit"])


def build_account_balance_history():
    balance_history_df = load_balances_history().copy()

    if balance_history_df.empty:
        return pd.DataFrame(
            columns=[
                "date",
            ]
        )

    balance_history_df["date"] = pd.to_datetime(balance_history_df["date"])
    pivot = balance_history_df.pivot(index="date", columns="account", values="balance")
    pivot = pivot.sort_index()
    pivot = pivot.reset_index()
    pivot.columns.name = None
    return pivot


def build_chart_dataframe(selected_accounts, selected_metrics):
    final_df = None

    if selected_accounts:
        balance_history = build_account_balance_history().copy()
        selected_accounts_history = balance_history.filter(
            items=["date"] + selected_accounts
        )
        final_df = selected_accounts_history
    if selected_metrics:
        net_worth_history_df = build_net_worth_history()
        net_worth_history_df = net_worth_history_df.filter(
            items=["date"] + selected_metrics
        )

        if final_df is not None:
            final_df = pd.merge(final_df, net_worth_history_df, on="date", how="outer")
        else:
            final_df = net_worth_history_df

    if final_df is not None:
        final_df = final_df.sort_values("date").reset_index(drop=True)
        return final_df
    else:
        return pd.DataFrame(columns=["date"])
