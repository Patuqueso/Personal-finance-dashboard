from enum import Enum


DEFAULT_GOALS = {"goals": [], "next_goal_id": 0}


class Status(Enum):
    ACTIVE = "active"
    WAITING = "waiting"
    READY = "ready"
    COMPLETED = "completed"
    INACTIVE = "inactive"


ALLOCATED_STATUSES = [Status.ACTIVE.value, Status.READY.value, Status.WAITING.value]

GOAL = {
    "id": None,
    "name": None,
    "target_amount": None,
    "current_amount": 0,
    "status": Status.ACTIVE.value,
    "date_completed": None,
}
