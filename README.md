📊 Personal Finance Dashboard

Local Streamlit dashboard for tracking:

Monthly spending

Categorized expenses

Assets vs liabilities

Net worth

Credit utilization

Financial trajectory over time

Runs fully locally. No APIs. No subscriptions.

🛠 Requirements

Python 3.12+

Virtual environment

pandas

plotly

streamlit

🚀 How to Run the Dashboard
1️⃣ Navigate to project folder
cd ~/finance_dashboard
2️⃣ Activate virtual environment
source venv/bin/activate

You should see:

(venv) patuqueso@...
3️⃣ Start Streamlit
streamlit run app.py

Then open:

http://localhost:8501
📂 Project Structure
finance_dashboard/
│
├── app.py
├── finance/
├── goals/
├── utils/
├── data/
│   ├── balances.csv
│   ├── goals.json
│   ├── net_worth_history.csv
│   ├── rules.csv
│   └── transactions/
│       ├── chequing.csv
│       ├── visa.csv
│       └── savings.csv
└── venv/
📥 Adding New Transaction Data

Each month:

1️⃣ Download CSVs from RBC

Export separately for:

Chequing

Credit card

Savings (if used)

Format must include:

Transaction Date
Description 1
Description 2
CAD$
2️⃣ Place CSV files into:
finance_dashboard/data/transactions/

You can:

Replace old files
or

Keep adding new ones (app concatenates all CSVs)

No manual cleaning needed.

3️⃣ Restart Streamlit (if running)

Stop with:

Ctrl + C

Then:

streamlit run app.py
💰 Updating Account Balances

Edit:

data/balances.csv

Format:

account,type,balance,limit
Chequing,Asset,2000,0
TFSA,Asset,5000,0
Credit Card,Liability,1200,5000
Student Loan,Liability,15000,0

type must be Asset or Liability

limit only needed for credit cards

📈 Saving Monthly Snapshot

At end of each month:

Update data/balances.csv

Click "Save Monthly Snapshot"

This updates:

data/net_worth_history.csv

Snapshots are stored by month (YYYY-MM).

If you click twice in same month → it overwrites.

🧠 Category Rules

Edit:

data/rules.csv

Format:

priority,match,category
100,uber,Transport
90,amazon prime,Subscriptions
80,amazon,G shopping
70,presto,Transport
...

Higher priority runs first

First match wins

No match → "Other"

🔒 Notes

Transfers and Interest & Fees are excluded from spending totals

Everything runs locally

No banking APIs

No external data transmission

🧘 Monthly Ritual

At month-end:

Download CSVs

Drop into /data

Update balances

Save snapshot

Review trajectory
