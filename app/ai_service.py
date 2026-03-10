import json
from .config import GEMINI_API_KEY


def generate_monthly_plan(user_profile: dict) -> list:
    """
    Generate a 30-day workout plan using Gemini API.
    Returns list of 30 days, each day is a list of exercise dicts:
    [{name, sets, reps, rest, video_url}, ...]
    Falls back to default plan if no API key.
    """
    if not GEMINI_API_KEY:
        return _default_monthly_plan(user_profile)

    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""Создай план тренировок на 30 дней для пользователя:
Имя: {user_profile.get('name')}
Возраст: {user_profile.get('age')} лет
Вес: {user_profile.get('weight')} кг
Рост: {user_profile.get('height')} см
Цель: {user_profile.get('goal')}
Уровень: {user_profile.get('experience')}
Дней в неделю: {user_profile.get('days_per_week')}
Оборудование: {user_profile.get('equipment')}

Верни ТОЛЬКО валидный JSON массив из 30 элементов (дни).
Каждый элемент — массив упражнений (от 1 до 6).
Каждое упражнение — объект с полями:
- name (string): название упражнения на русском
- sets (int): количество подходов
- reps (string): повторения или время, например "12" или "60 сек"
- rest (int): отдых между подходами в секундах
- video_url (string): ссылка на YouTube видео с техникой (реальная или пустая строка)

Дни отдыха — пустой массив [].
Пример одного дня: [{"name": "Приседания", "sets": 3, "reps": "12", "rest": 60, "video_url": ""}]

Верни только JSON, без пояснений."""

    response = model.generate_content(prompt)
    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        plan = json.loads(text)
        if isinstance(plan, list) and len(plan) == 30:
            return plan
    except (json.JSONDecodeError, ValueError):
        pass

    return _default_monthly_plan(user_profile)


def _default_monthly_plan(user_profile: dict) -> list:
    """Hardcoded 30-day plan cycling through exercise groups."""
    goal = user_profile.get("goal", "Поддержание формы")
    days_per_week = int(user_profile.get("days_per_week", 3))

    templates = {
        "Похудение": [
            [
                {"name": "Приседания", "sets": 4, "reps": "15", "rest": 45, "video_url": ""},
                {"name": "Отжимания", "sets": 3, "reps": "12", "rest": 45, "video_url": ""},
                {"name": "Планка", "sets": 3, "reps": "60 сек", "rest": 30, "video_url": ""},
                {"name": "Бурпи", "sets": 3, "reps": "10", "rest": 60, "video_url": ""},
            ],
            [
                {"name": "Выпады", "sets": 3, "reps": "12", "rest": 45, "video_url": ""},
                {"name": "Отжимания на трицепс", "sets": 3, "reps": "12", "rest": 45, "video_url": ""},
                {"name": "Подъёмы ног лёжа", "sets": 3, "reps": "15", "rest": 30, "video_url": ""},
                {"name": "Прыжки на месте", "sets": 4, "reps": "30 сек", "rest": 30, "video_url": ""},
            ],
            [
                {"name": "Становая тяга", "sets": 3, "reps": "12", "rest": 60, "video_url": ""},
                {"name": "Тяга гантелей", "sets": 3, "reps": "12", "rest": 60, "video_url": ""},
                {"name": "Скручивания", "sets": 3, "reps": "20", "rest": 30, "video_url": ""},
            ],
        ],
        "Набор массы": [
            [
                {"name": "Жим лёжа", "sets": 4, "reps": "8", "rest": 90, "video_url": ""},
                {"name": "Разводка гантелей", "sets": 3, "reps": "12", "rest": 60, "video_url": ""},
                {"name": "Французский жим", "sets": 4, "reps": "10", "rest": 60, "video_url": ""},
            ],
            [
                {"name": "Тяга штанги", "sets": 4, "reps": "8", "rest": 90, "video_url": ""},
                {"name": "Тяга верхнего блока", "sets": 4, "reps": "10", "rest": 60, "video_url": ""},
                {"name": "Подъём гантелей на бицепс", "sets": 4, "reps": "12", "rest": 60, "video_url": ""},
            ],
            [
                {"name": "Приседания со штангой", "sets": 4, "reps": "8", "rest": 90, "video_url": ""},
                {"name": "Жим ногами", "sets": 4, "reps": "10", "rest": 90, "video_url": ""},
                {"name": "Разгибания ног", "sets": 3, "reps": "12", "rest": 60, "video_url": ""},
            ],
        ],
        "Сила": [
            [
                {"name": "Приседания со штангой", "sets": 5, "reps": "5", "rest": 180, "video_url": ""},
                {"name": "Жим лёжа", "sets": 5, "reps": "5", "rest": 180, "video_url": ""},
            ],
            [
                {"name": "Становая тяга", "sets": 5, "reps": "5", "rest": 180, "video_url": ""},
                {"name": "Жим стоя", "sets": 5, "reps": "5", "rest": 180, "video_url": ""},
            ],
            [
                {"name": "Приседания со штангой", "sets": 3, "reps": "3", "rest": 240, "video_url": ""},
                {"name": "Жим лёжа", "sets": 3, "reps": "3", "rest": 240, "video_url": ""},
                {"name": "Становая тяга", "sets": 3, "reps": "3", "rest": 240, "video_url": ""},
            ],
        ],
        "Поддержание формы": [
            [
                {"name": "Приседания", "sets": 3, "reps": "12", "rest": 60, "video_url": ""},
                {"name": "Отжимания", "sets": 3, "reps": "12", "rest": 60, "video_url": ""},
                {"name": "Планка", "sets": 3, "reps": "45 сек", "rest": 30, "video_url": ""},
            ],
            [
                {"name": "Тяга гантелей", "sets": 3, "reps": "12", "rest": 60, "video_url": ""},
                {"name": "Жим гантелей лёжа", "sets": 3, "reps": "12", "rest": 60, "video_url": ""},
                {"name": "Скручивания", "sets": 3, "reps": "20", "rest": 30, "video_url": ""},
            ],
        ],
    }

    base = templates.get(goal, templates["Поддержание формы"])
    plan = []
    workout_day = 0

    for day_num in range(30):
        week_day = day_num % 7
        if week_day < days_per_week:
            plan.append(base[workout_day % len(base)])
            workout_day += 1
        else:
            plan.append([])

    return plan


def get_ai_motivation(exercise_name: str, sets_done: int, total_sets: int) -> str:
    """Return a short motivational message (no API call)."""
    if sets_done == 0:
        return f"Начинаем {exercise_name}! Ты справишься 💪"
    if sets_done < total_sets:
        remaining = total_sets - sets_done
        return f"Отлично! Осталось {remaining} подход(а). Держись! 🔥"
    return f"Упражнение завершено! Отличная работа 🎉"
