import pandas as pd
from .history import load_balances_history
from utils import BALANCES_FILE, BALANCES_HISTORY_FILE


def load_balances():
    if BALANCES_FILE.exists():
        df = pd.read_csv(BALANCES_FILE)

        df["balance"] = pd.to_numeric(df["balance"], errors="coerce").fillna(0)
        df["limit"] = pd.to_numeric(df["limit"], errors="coerce").fillna(0)

        return df

    return pd.DataFrame(columns=["account", "type", "balance", "limit"])


def calculate_financial_position(balances_df):
    assets_df = balances_df[balances_df["type"] == "Asset"].copy()
    liabilities_df = balances_df[balances_df["type"] == "Liability"].copy()

    total_assets = assets_df["balance"].sum()
    total_liabilities = liabilities_df["balance"].sum()

    net_worth = total_assets - total_liabilities

    return {
        "assets_df": assets_df,
        "liabilities_df": liabilities_df,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": net_worth,
    }


def calculate_credit_utilization(balances_df):
    credit_row = balances_df[balances_df["account"] == "Credit Card"]

    if not credit_row.empty and credit_row["limit"].iloc[0] > 0:
        balance = credit_row["balance"].iloc[0]
        limit = credit_row["limit"].iloc[0]

        utilization = balance / limit
        return utilization

    return None


def update_all_balances(updated_balances):
    balances_df = load_balances().copy()

    for account_name, new_balance in updated_balances.items():
        if account_name not in balances_df["account"].values:
            print("Account: " + account_name + " not found")
            return None

        if new_balance < 0:
            print("Value must be bigger than or equal to 0")
            return None

    record_balance_snapshot()

    for account_name, new_balance in updated_balances.items():
        balances_df.loc[balances_df["account"] == account_name, "balance"] = new_balance

    balances_df.to_csv(BALANCES_FILE, index=False)
    print("Balance updated!")
    return None


def record_balance_snapshot():
    balances_df = load_balances()
    balances_history_df = load_balances_history()

    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    balances_snapshot_df = balances_df.copy()
    balances_snapshot_df.insert(loc=0, column="date", value=today)
    new_balances_history = pd.concat([balances_history_df, balances_snapshot_df])

    new_balances_history.to_csv(BALANCES_HISTORY_FILE, index=False)


def get_balance_by_account(account_name):
    balances_df = load_balances()

    balance_row = balances_df[balances_df["account"] == account_name]
    if balance_row.empty:
        print("No account with name: " + account_name + ", does not exist.")
        return None

    balance = balance_row.iloc[0]
    balance_dict = balance.to_dict()

    return balance_dict


# record_balance_snapshot()
