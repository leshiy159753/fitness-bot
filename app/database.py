from datetime import datetime
from typing import Optional

# In-memory database
# users[telegram_id] = {
#   name, age, weight, height, goal, experience, days_per_week, equipment,
#   monthly_plan: list[list[dict]],  # 30 days x exercises
#   current_day: int,                # 0-indexed current day
#   current_exercise_idx: int,       # index within today's exercises
#   today_sets: list[dict],          # [{reps, weight}, ...] for current exercise
#   workout_log: list[dict]          # [{date, exercise, sets:[{reps,weight}]}, ...]
# }
users: dict = {}


def get_user(telegram_id: int) -> Optional[dict]:
    """Get user data by telegram_id. Returns None if not found."""
    return users.get(telegram_id)


def save_user(telegram_id: int, data: dict) -> None:
    """Save or update user data."""
    if telegram_id in users:
        users[telegram_id].update(data)
    else:
        users[telegram_id] = {
            "workout_log": [],
            "monthly_plan": [],
            "current_day": 0,
            "current_exercise_idx": 0,
            "today_sets": [],
            **data,
        }


def log_exercise_sets(telegram_id: int, exercise: str, sets: list) -> None:
    """
    Add a completed exercise entry to the user's workout log.
    sets: list of {reps: int, weight: float|None}
    """
    if telegram_id not in users:
        return
    entry = {
        "date": datetime.now().strftime("%d.%m.%Y"),
        "exercise": exercise,
        "sets": sets,
    }
    users[telegram_id].setdefault("workout_log", []).append(entry)


def get_workout_history(telegram_id: int, limit: int = 10) -> list:
    """Get last N workout log entries for a user."""
    user = users.get(telegram_id)
    if not user:
        return []
    log = user.get("workout_log", [])
    return log[-limit:]


def advance_exercise(telegram_id: int) -> bool:
    """
    Move to the next exercise in today's plan.
    Returns True if there is a next exercise, False if the day is done.
    """
    user = users.get(telegram_id)
    if not user:
        return False
    plan = user.get("monthly_plan", [])
    day_idx = user.get("current_day", 0)
    if not plan or day_idx >= len(plan):
        return False
    today = plan[day_idx]
    next_idx = user.get("current_exercise_idx", 0) + 1
    if next_idx < len(today):
        user["current_exercise_idx"] = next_idx
        user["today_sets"] = []
        return True
    return False


def finish_day(telegram_id: int) -> None:
    """Advance to the next day and reset exercise index."""
    user = users.get(telegram_id)
    if not user:
        return
    user["current_day"] = user.get("current_day", 0) + 1
    user["current_exercise_idx"] = 0
    user["today_sets"] = []
