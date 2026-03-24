from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TRANSACTIONS_DIR = DATA_DIR / "transactions"

BALANCES_FILE = DATA_DIR / "balances.csv"
BALANCES_HISTORY_FILE = DATA_DIR / "balances_history.csv"
RULES_FILE = DATA_DIR / "rules.csv"
HISTORY_FILE = DATA_DIR / "net_worth_history.csv"
GOALS_FILE = DATA_DIR / "goals.json"
