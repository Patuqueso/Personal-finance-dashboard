# Personal Finance Dashboard

A Streamlit dashboard for reviewing transaction history, categorizing spending, tracking balances over time, and managing savings goals.

## What the app does

The dashboard is split into four main sections:

- Financial position: reads your account balances, shows total assets, liabilities, net worth, and credit utilization.
- Historical data and trajectory: stores balance snapshots and charts net worth, credit utilization, and individual account balances over time.
- Goals and allocations: tracks savings goals and compares allocated goal money against your savings balance, while reserving a built-in emergency fund.
- Monthly spending: loads transaction CSVs, auto-categorizes them with keyword rules, and shows income, spending totals, a category pie chart, and the raw transactions for the selected month.

## Project structure

```text
finance_dashboard/
├── app.py
├── finance/
│   ├── balances.py
│   ├── history.py
│   └── transactions.py
├── goals/
│   ├── model.py
│   ├── operations.py
│   └── storage.py
├── utils/
│   ├── categorization.py
│   └── paths.py
├── data/
│   ├── transactions/
│   ├── balances.csv
│   ├── balances_history.csv
│   ├── goals.json
│   ├── rules_example.csv
│   └── config.json
└── README.md
```

## Requirements

- Python 3.10+
- `streamlit`
- `pandas`
- `plotly`

Install them with:

```bash
pip install streamlit pandas plotly
```

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/Patuqueso/Personal-finance-dashboard.git
cd finance_dashboard
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Prepare the data files

The app reads from files inside `data/`.

The repository already includes fake sample data for transactions, rules, balances, balance history, and goals so you can run the dashboard immediately.

If you want to replace the sample transaction data with your own file, put one or more CSVs in `data/transactions/`.

If you want to rebuild the rules file from the example copy, use:

```bash
cp data/rules_example.csv data/rules.csv
```

You can keep multiple transaction CSV files in `data/transactions/`. The app loads every `.csv` file in that folder and combines them.

### 4. Add balances

The repo already includes a fake `data/balances.csv`. If you want to replace it, use this structure:

```csv
account,type,balance,limit
Chequing,Asset,2500,0
Savings,Asset,8000,0
Credit Card,Liability,1200,5000
```

Notes:

- `type` must be `Asset` or `Liability`.
- `limit` is mainly used for the `Credit Card` row so the app can calculate credit utilization.
- The goals allocation summary specifically looks for an account named `Savings`.

### 5. Run the app

```bash
streamlit run app.py
```

## Data files

### `data/transactions/*.csv`

The app expects RBC-style transaction exports and combines all CSV files in `data/transactions/`.

Important columns used by the code:

- `Transaction Date`
- `Description 1`
- `Description 2`
- `CAD$`

What happens during loading:

- `Transaction Date` is converted to a month label used in the sidebar filter.
- `Description 1` and `Description 2` are merged into a single description.
- `CAD$` is renamed to `Amount`.
- Rules from `data/rules.csv` are used to assign categories.

Important format note:

- The loader currently parses `Transaction Date` using `MM/DD/YYYY`.
- If your CSV uses another format, those rows may be skipped unless you convert the dates first.

### `data/rules.csv`

This file is required for categorization. The repository includes `data/rules_example.csv`, but the app reads `data/rules.csv`.

Expected columns:

```csv
priority,match,category
100,e-transfer sent,Transfer
90,uber,Transport
80,grocery store,Groceries
45,payroll deposit,Income
```

How rules work:

- Rules are matched against the lowercased transaction description.
- Higher `priority` values are checked first.
- The first matching rule wins.
- If nothing matches, the transaction is categorized as `Other`.

### `data/balances.csv`

Used for:

- assets vs. liabilities tables
- net worth
- credit utilization
- savings allocation summary

The repository includes a fake sample file with:

- `Chequing`
- `Savings`
- `TFSA`
- `Credit Card`
- `Student Loan`

Expected columns:

```csv
account,type,balance,limit
Chequing,Asset,2500,0
Savings,Asset,8000,0
Credit Card,Liability,1200,5000
```

### `data/balances_history.csv`

Stores historical balance snapshots. The dashboard updates this file when you use the balance update controls in the app.

The repository includes fake monthly snapshots from November 30, 2025 through March 23, 2026 so the history charts render immediately.

Expected columns:

```csv
date,account,type,balance,limit
2026-03-23,Chequing,Asset,2500,0
2026-03-23,Savings,Asset,8000,0
2026-03-23,Credit Card,Liability,1200,5000
```

If this file is empty, the historical charts will stay blank until you update balances in the UI.

### `data/goals.json`

Stores your goal list and the next available goal ID.

The repository includes fake goals that showcase every supported status:

- `active`
- `waiting`
- `ready`
- `completed`
- `inactive`

File structure:

```json
{
  "goals": [
    {
      "id": 0,
      "name": "Car Fund",
      "target_amount": 20000,
      "current_amount": 0,
      "status": "active",
      "date_completed": null
    }
  ],
  "next_goal_id": 1
}
```

The dashboard displays and manages goals already present in this file.

## Goals and allocation logic

The allocation summary is based on your `Savings` account balance.

Current behavior in code:

- Savings balance is pulled from the account named `Savings`.
- A fixed emergency fund of $3000 is reserved (configurable in future versions).
- Goal amounts with status `active`, `waiting`, or `ready` count as allocated.
- Remaining allocatable money is calculated as:

```text
Savings - Emergency Fund - Allocated Goal Money
```

If the remaining value drops below zero, the app shows an overallocation warning.

## What is included in this repo

- Fake transaction data: [data/transactions/transaction_example.csv](/home/patuqueso/finance_dashboard/data/transactions/transaction_example.csv)
- Fake categorization rules: [data/rules.csv](/home/patuqueso/finance_dashboard/data/rules.csv)
- Copyable rules example: [data/rules_example.csv](/home/patuqueso/finance_dashboard/data/rules_example.csv)
- Fake balances: [data/balances.csv](/home/patuqueso/finance_dashboard/data/balances.csv)
- Fake balance history: [data/balances_history.csv](/home/patuqueso/finance_dashboard/data/balances_history.csv)
- Fake goals data: [data/goals.json](/home/patuqueso/finance_dashboard/data/goals.json)

## Known setup details

- The sample balances and goals are intentionally set up so the allocation summary shows an overallocated state. This helps demonstrate the warning UI.
- The dashboard stops early if no transaction CSV files are found in `data/transactions/`.

## Tech stack

- Streamlit
- Pandas
- Plotly
