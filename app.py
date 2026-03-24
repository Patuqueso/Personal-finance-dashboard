import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# IMPORTS FROM MODULES
from finance import (
    load_transactions,
    load_balances,
    calculate_financial_position,
    calculate_credit_utilization,
    update_all_balances,
    record_balance_snapshot,
    build_chart_dataframe,
    build_account_balance_history,
)

from goals import (
    load_goals,
    add_money_to_goal,
    add_money_to_goal,
    get_allocation_summary,
    update_goal_target,
    remove_money_from_goal,
)
from utils import load_rules, categorize


st.set_page_config(layout="wide")
st.title("Personal Finance Dashboard")


# =====================================================
# LOAD TRANSACTIONS
# =====================================================

df = load_transactions()

if df.empty:
    st.warning("No CSV files found in `data/transactions`.")
    st.stop()


# =====================================================
# APPLY CATEGORIZATION
# =====================================================

rules_df = load_rules()
df["Category"] = df["Description"].apply(lambda x: categorize(x, rules_df))


# =====================================================
# SIDEBAR FILTER
# =====================================================

st.sidebar.header("Filters")

months = sorted(df["Month"].unique(), reverse=True)
selected_month = st.sidebar.selectbox("Select Month", months)

month_df = df[df["Month"] == selected_month]


# =====================================================
# LOAD BALANCES
# =====================================================

balances_df = load_balances()

if not balances_df.empty:
    finance_data = calculate_financial_position(balances_df)

    total_assets = finance_data["total_assets"]
    total_liabilities = finance_data["total_liabilities"]
    net_worth = finance_data["net_worth"]

    assets_df = finance_data["assets_df"]
    liabilities_df = finance_data["liabilities_df"]

    utilization = calculate_credit_utilization(balances_df)

    # =====================================================
    # FINANCIAL POSITION
    # =====================================================

    st.subheader("Financial Position")

    colA, colB, colC = st.columns(3)

    colA.metric("Total Assets", f"${total_assets:,.2f}")
    colB.metric("Total Liabilities", f"${total_liabilities:,.2f}")
    colC.metric("Net Worth", f"${net_worth:,.2f}")

    # =====================================================
    # MANAGE BALANCES
    # =====================================================
    with st.expander("⚙️ Manage Balances"):
        col1, col2 = st.columns(2)
        assets = balances_df[balances_df["type"] == "Asset"]
        liabilities = balances_df[balances_df["type"] == "Liability"]
        account_dict = {}

        with col1:
            st.markdown("**Assets**")
            for row in assets.itertuples(index=False):
                label_col, input_col = st.columns([1, 3])

                label_col.text(row.account)

                val = input_col.number_input(
                    f"{row.account} balance",
                    label_visibility="collapsed",
                    min_value=0.0,
                    value=row.balance,
                    step=1.0,
                    key=row.account,
                )

                account_dict[row.account] = val

        with col2:
            st.markdown("**Liabilities**")
            for row in liabilities.itertuples(index=False):
                label_col, input_col = st.columns([1, 3])

                label_col.text(row.account)

                val = input_col.number_input(
                    f"{row.account} balance",
                    label_visibility="collapsed",
                    min_value=0.0,
                    value=row.balance,
                    step=1.0,
                    key=row.account,
                )

                account_dict[row.account] = val

        # BUTTON
        if st.button("Update Balances", width="stretch"):
            update_all_balances(account_dict)
            record_balance_snapshot()
            st.success("Balances updated successfully!")
            st.rerun()

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Assets")
        st.dataframe(assets_df, width="stretch")

    with col2:
        st.markdown("### Liabilities")
        st.dataframe(liabilities_df, width="stretch")

    if utilization is not None:

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=utilization * 100,
                number={"suffix": "%"},
                title={"text": "Credit Utilization"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, 30], "color": "#2ecc71"},
                        {"range": [30, 50], "color": "#f1c40f"},
                        {"range": [50, 100], "color": "#e74c3c"},
                    ],
                },
            )
        )

        st.plotly_chart(fig_gauge, width="stretch")

# =====================================================
# HISTORICAL DATA & TRAJECTORY
# =====================================================

st.divider()
st.subheader("Historical Data & Trajectory")

hist_col1, hist_col2 = st.columns([1, 2])

metrics = []
accounts = []

with hist_col1:
    st.markdown("Metrics")
    net_worth_checkbox = st.checkbox("Net Worth", key="n", value=True)
    credit_utilization_checkbox = st.checkbox("Credit Utilization", key="c")

    if net_worth_checkbox:
        metrics.append("net_worth")
    if credit_utilization_checkbox:
        metrics.append("credit_utilization")

with hist_col2:
    st.markdown("Accounts")
    col1, col2 = st.columns(2)
    account_history_df = build_account_balance_history()
    cols = [col1, col2]
    iter = 0
    for account in account_history_df.columns.drop("date"):
        col = cols[iter % 2]
        with col:
            account_checkbox = st.checkbox(account, key=account + "chbx")
            if account_checkbox:
                accounts.append(account)
        iter += 1

history_df = build_chart_dataframe(
    selected_accounts=accounts,
    selected_metrics=metrics,
)

if not history_df.empty:
    history_df = history_df.sort_values("date")

    needs_percentage = "credit_utilization" in history_df.columns

    fig_traj = go.Figure()

    for choice in history_df.columns.drop("date"):
        if choice == "credit_utilization":
            fig_traj.add_trace(
                go.Scatter(
                    x=history_df["date"],
                    y=history_df[choice],
                    mode="lines+markers",
                    line=dict(dash="dash"),
                    name=choice.replace("_", " ").title(),
                    yaxis="y2",
                    hovertemplate=choice.replace("_", " ").title()
                    + ": %{y}<extra></extra>",
                )
            )

        else:
            fig_traj.add_trace(
                go.Scatter(
                    x=history_df["date"],
                    y=history_df[choice],
                    name=choice.replace("_", " ").title(),
                    mode="lines+markers",
                    hovertemplate=choice.replace("_", " ").title()
                    + ": $"
                    + "%{y:,.2f}<extra></extra>",
                )
            )

    fig_traj.update_layout(
        title="Financial Trajectory",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Amount ($ CAD)", side="left"),
        legend=dict(x=0.01, y=1.1, orientation="h"),
        yaxis_tickformat="$,.2f",
    )

    if needs_percentage:
        fig_traj.update_layout(
            yaxis2=dict(
                title="Credit Utilization (%)",
                overlaying="y",
                side="right",
                range=[0, 100],
            ),
            yaxis2_tickformat=".0f",
            yaxis2_ticksuffix="%",
            hovermode="x",
        )

    st.plotly_chart(fig_traj, width="stretch")

else:
    st.info(
        "No historical data available. Update your balances to start tracking your financial position over time."
    )

# =====================================================
# GOALS & ALLOCATIONS
# =====================================================
st.divider()
st.subheader("Goals & Allocations")


allocation_summary = get_allocation_summary()
emergency_fund = allocation_summary["emergency_fund"]
allocated_amount = allocation_summary["allocated"]
savings_balance = allocation_summary["savings_balance"]
remaining_amount = allocation_summary["remaining"]


if remaining_amount < 0:
    st.warning(
        f" You are currently overallocated by ${abs(remaining_amount):,.2f}", icon="⚠️"
    )


col1, col2, col3, col4 = st.columns(4)

col1.metric("Current Savings", f"${savings_balance:,.2f}")
col2.metric("Allocated", f"${allocated_amount:,.2f}")
col3.metric("Remaining", f"${remaining_amount:,.2f}")
col4.metric("Emergency Fund", f"${emergency_fund:,.2f}")

goals = load_goals()

completed_goals = [goal for goal in goals["goals"] if goal["status"] == "completed"]
incomplete_goals = [goal for goal in goals["goals"] if goal["status"] != "completed"]

if not goals["goals"]:
    st.info("No goals set yet.")

# color mapping
color_map = {
    "active": "#1f77b4",  # blue
    "ready": "#2ecc71",  # green
    "waiting": "#f39c12",  # orange
    "completed": "#9b59b6",  # purple
    "inactive": "#7f8c8d",  # gray
}

for goal in incomplete_goals:
    col1, col2 = st.columns([1, 1])
    status = goal["status"].lower()
    color = color_map.get(status, "#7f8c8d")

    # Badge + Name (inline)
    with col1:
        st.html(
            f"""
            <div style="display: flex; align-items: center; gap: 6px; flex-direction: column; align-items: flex-start;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="
                        background-color: {color};
                        color: white;
                        padding: 2px 6px;
                        border-radius: 8px;
                        font-size: 0.65rem;
                        font-weight: 600;
                    ">
                        {status.upper()}
                    </span>
                    <span style="font-size: 1rem; font-weight: 600;">
                        {goal['name']}
                    </span>
                </div>
                <span style="color: white">
                    ${goal['current_amount']:,.2f} / ${goal['target_amount']:,.2f}
                </span>
            </div>
            """
        )

        # Progress bar
        sub_col1, sub_col2 = st.columns([2, 1])
        with sub_col1:
            progress = min(goal["current_amount"] / goal["target_amount"], 1.0)
            st.progress(progress)
            manage_col, empty = st.columns([2, 1])
            with manage_col:
                with st.expander("Manage Goal"):
                    new_target = st.number_input(
                        "Target",
                        min_value=0.0,
                        value=float(goal["target_amount"]),
                        step=1.0,
                    )
                    if st.button("Update Target", key=goal["name"] + "_new_target"):
                        update_goal_target(goal["name"], new_target)
                        st.success("Target updated successfully!")
                        st.rerun()

                    st.markdown("---")

                    amount_input = st.number_input(
                        "Funds",
                        min_value=0.0,
                        value=0.0,
                        step=1.0,
                        key=goal["name"] + "_add_amount_input",
                    )
                    amount_container = st.container(horizontal=True)

                    with amount_container:
                        if st.button("Add", key=goal["name"] + "_add_amount"):
                            add_money_to_goal(goal["id"], amount_input)
                            st.success("Amount added successfully!")
                            st.rerun()
                        if st.button("Remove", key=goal["name"] + "_remove_amount"):
                            remove_money_from_goal(goal["id"], amount_input)
                            st.success("Amount subtracted successfully!")
                            st.rerun()
        with sub_col2:
            st.text(f"{progress * 100:.1f}%")


with st.expander("View Completed Goals"):
    for goal in completed_goals:
        col1, col2 = st.columns([1, 5])
        with col1:
            st.html(
                f"""
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="
                        background-color: {color_map['completed']};
                        color: white;
                        padding: 2px 6px;
                        border-radius: 8px;
                        font-size: 0.65rem;
                        font-weight: 600;
                    ">
                        COMPLETED
                    </span>
                    <span style="font-size: 1rem; font-weight: 600;">
                        {goal['name']}
                    </span>
                </div>
                """
            )

            st.text(f"${goal['current_amount']:,.2f} / ${goal['target_amount']:,.2f}")
        with col2:
            sub_col1, sub_col2 = st.columns([4, 1])
            with sub_col1:
                st.markdown("Completed on: " + f"{goal['date_completed']}")
                st.progress(1.0)
            with sub_col2:
                st.html("<br>")
                st.text(f"{progress * 100:.1f}%")

# =====================================================
# MONTHLY SPENDING
# =====================================================

st.divider()
expenses = month_df[
    (month_df["Amount"] < 0)
    & (~month_df["Category"].isin(["Transfer", "Interest & Fees"]))
]

income = month_df[(month_df["Amount"] > 0) & (~month_df["Category"].isin(["Transfer"]))]

st.subheader(f"Monthly Spending — {selected_month}")

col1, col2 = st.columns(2)

col1.metric("Total Spent", f"${abs(expenses['Amount'].sum()):,.2f}")
col2.metric("Total Income", f"${income['Amount'].sum():,.2f}")

expenses_grouped = expenses.groupby("Category")["Amount"].sum().abs().reset_index()

if not expenses_grouped.empty:

    fig_spending = px.pie(
        expenses_grouped,
        names="Category",
        values="Amount",
        title="Spending Breakdown",
    )

    st.plotly_chart(fig_spending, width="stretch")


# =====================================================
# RAW TRANSACTIONS
# =====================================================

with st.expander("View Raw Transactions"):

    st.dataframe(
        month_df[["Transaction Date", "Description", "Category", "Amount"]].sort_values(
            "Transaction Date", ascending=False
        ),
        width="stretch",
    )

st.divider()
