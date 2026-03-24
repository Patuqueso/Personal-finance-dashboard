import copy
import json
from goals import DEFAULT_GOALS
from utils import GOALS_FILE


def load_goals():
    if GOALS_FILE.exists():
        with open(GOALS_FILE, "r") as goals:
            return json.load(goals)
    else:
        with open(GOALS_FILE, "w") as goals:
            tmp_goals = copy.deepcopy(DEFAULT_GOALS)
            json.dump(tmp_goals, goals)
            return tmp_goals


def save_goals(updated_goals):
    with open(GOALS_FILE, "w") as goals:
        json.dump(updated_goals, goals, indent=4)
