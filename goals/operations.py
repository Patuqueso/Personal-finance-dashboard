import copy
from datetime import datetime

from finance import load_balances
from .model import ALLOCATED_STATUSES, GOAL, Status
from .storage import load_goals, save_goals


def add_goal(name, target_amount):
    goals_dictionary = load_goals()
    new_goal = copy.deepcopy(GOAL)
    new_goal["id"] = goals_dictionary["next_goal_id"]
    goals_dictionary["next_goal_id"] += 1
    new_goal["name"] = name
    new_goal["target_amount"] = target_amount
    goals_dictionary["goals"].append(new_goal)
    save_goals(goals_dictionary)


def get_goal_by_id(goals_dictionary, goal_id):
    goals = goals_dictionary["goals"]
    for goal in goals:
        if goal["id"] == goal_id:
            return goal

    return None


def update_goal_target(goal_id, new_target):
    goals_dictionary = load_goals()
    goal = get_goal_by_id(goals_dictionary, goal_id)
    if goal is None:
        print("Goal with id(" + str(goal_id) + ") does not exist.")
        return

    if new_target <= 0:
        print("Target must be bigger than $0")
        return
    elif new_target >= 1000000:
        print("Please be realistic")
        return
    elif goal["current_amount"] >= new_target:
        print("Warning: Goal target has been reached or exceeded")
        goal["status"] = Status.READY.value

    goal["target_amount"] = new_target
    save_goals(goals_dictionary)


def add_money_to_goal(goal_id, amount):
    goals_dictionary = load_goals()

    if amount <= 0:
        print("Amount must be bigger than $0")
        return

    goal = get_goal_by_id(goals_dictionary, goal_id)
    if goal is None:
        print(f"Goal with id({goal_id}) does not exist.")
        return

    goal["current_amount"] += amount

    if goal["current_amount"] == goal["target_amount"]:
        print("Goal fully funded!")
        goal["status"] = Status.READY.value

    elif goal["current_amount"] > goal["target_amount"]:
        print("Warning: Goal overfunded.")
        goal["status"] = Status.READY.value

    save_goals(goals_dictionary)

    # ⚠️ Warning only (no blocking)
    summary = get_allocation_summary()
    if summary["remaining"] < 0:
        print("⚠️ You are overallocated after this operation.")


def remove_money_from_goal(goal_id, amount):
    goals_dictionary = load_goals()

    if amount <= 0:
        print("Amount must be bigger than $0")
        return

    goal = get_goal_by_id(goals_dictionary, goal_id)
    if goal is None:
        print(f"Goal with id({goal_id}) does not exist.")
        return

    if amount > goal["current_amount"]:
        print("Amount to remove exceeds current allocated amount.")
        return

    goal["current_amount"] -= amount

    if goal["current_amount"] < goal["target_amount"]:
        goal["status"] = Status.ACTIVE.value

    save_goals(goals_dictionary)

    # ⚠️ Warning only (no blocking)
    summary = get_allocation_summary()
    if summary["remaining"] < 0:
        print("⚠️ You are overallocated after this operation.")


def get_allocation_summary():
    balances_df = load_balances()
    goals = load_goals()
    savings_balance = sum(balances_df[balances_df["account"] == "Savings"]["balance"])

    emergency_fund = 3000
    allocated_amount = 0
    for goal in goals["goals"]:
        if goal["status"] in ALLOCATED_STATUSES:
            allocated_amount += goal["current_amount"]

    available_amount = savings_balance - emergency_fund
    remaining_amount = available_amount - allocated_amount

    if remaining_amount < 0:
        print("Warning: No funds available for allocation. ")

    return {
        "savings_balance": savings_balance,
        "emergency_fund": emergency_fund,
        "allocated": allocated_amount,
        "available": available_amount,
        "remaining": remaining_amount,
        "is_overallocated": remaining_amount < 0,
    }


def complete_goal(goal_id):
    goals_dictionary = load_goals()

    goal = get_goal_by_id(goals_dictionary, goal_id)
    if goal is None:
        print(f"Goal with id({goal_id}) does not exist.")
        return

    if goal["status"] != Status.READY.value:
        print("Goal must be fully funded before completing.")
        return

    goal["status"] = Status.COMPLETED.value
    goal["date_completed"] = datetime.now().strftime("%Y-%m-%d")

    save_goals(goals_dictionary)

    # ⚠️ Warning if allocation still exists
    if goal["current_amount"] > 0:
        print(
            "⚠️ This goal still has allocated funds. Did you forget to update balances?"
        )


# add_goal("Car Fund", 20000)
# add_goal("Desk", 1200)
# add_goal("Trip", 3000)

# print(get_goal_by_id(2))
