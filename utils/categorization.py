import pandas as pd
from utils.paths import RULES_FILE


def load_rules():
    if RULES_FILE.exists():
        rules = pd.read_csv(RULES_FILE)

        rules["priority"] = (
            pd.to_numeric(rules["priority"], errors="coerce").fillna(0).astype(int)
        )

        rules["match"] = rules["match"].fillna("").astype(str)
        rules["category"] = rules["category"].fillna("Other").astype(str)

        return rules.sort_values("priority", ascending=False)

    return pd.DataFrame(columns=["priority", "match", "category"])


def categorize(description: str, rules_df) -> str:
    desc = (description or "").lower()

    for _, rule in rules_df.iterrows():
        if rule["match"].lower() in desc:
            return rule["category"]

    return "Other"
