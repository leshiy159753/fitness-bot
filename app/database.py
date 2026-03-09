from datetime import datetime
from typing import Optional

# In-memory database
# users[telegram_id] = {name, age, weight, height, goal, experience, days_per_week, equipment, program, workout_log: []}
users: dict = {}


def get_user(telegram_id: int) -> Optional[dict]:
    """Get user data by telegram_id. Returns None if not found."""
    return users.get(telegram_id)


def save_user(telegram_id: int, data: dict) -> None:
    """Save or update user data."""
    if telegram_id in users:
        users[telegram_id].update(data)
    else:
        users[telegram_id] = {"workout_log": [], **data}


def log_workout(
    telegram_id: int,
    exercise: str,
    sets: int,
    reps: int,
    weight: Optional[float] = None,
) -> None:
    """Add a workout entry to the user's log."""
    if telegram_id not in users:
        return
    entry = {
        "exercise": exercise,
        "sets": sets,
        "reps": reps,
        "weight": weight,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    users[telegram_id].setdefault("workout_log", []).append(entry)


def get_workout_history(telegram_id: int, limit: int = 10) -> list:
    """Get last N workout log entries for a user."""
    user = users.get(telegram_id)
    if not user:
        return []
    log = user.get("workout_log", [])
    return log[-limit:]
