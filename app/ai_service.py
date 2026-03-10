import json
import re
from .config import GEMINI_API_KEY

# Библиотека реальных YouTube видео по упражнениям
EXERCISE_VIDEOS = {
    "жим штанги лёжа": "https://youtu.be/rT7DgCr-3pg",
    "жим гантелей лёжа": "https://youtu.be/VmB1G1K7v94",
    "разводка гантелей": "https://youtu.be/eozdVDA78K0",
    "отжимания": "https://youtu.be/IODxDxX7oi4",
    "отжимания на брусьях": "https://youtu.be/2z8JmcrW-As",
    "жим в наклоне": "https://youtu.be/jPLdzuHckI8",
    "кроссовер": "https://youtu.be/taI4XduLpTk",
    "пуловер": "https://youtu.be/FK4rHfFCqTI",
    "подтягивания": "https://youtu.be/eGo4IYlbE5g",
    "тяга штанги в наклоне": "https://youtu.be/G8l_8chR5BE",
    "тяга гантели": "https://youtu.be/roCP6wCXPqo",
    "тяга блока": "https://youtu.be/GZbfZ033f74",
    "тяга верхнего блока": "https://youtu.be/CAwf7n6Luuc",
    "горизонтальная тяга": "https://youtu.be/GZbfZ033f74",
    "гиперэкстензия": "https://youtu.be/ph3pddpKzzw",
    "шраги": "https://youtu.be/g6qbq4Lf1FI",
    "жим штанги стоя": "https://youtu.be/2yjwXTZQDDI",
    "жим гантелей сидя": "https://youtu.be/qEwKCR5JCog",
    "разводка в стороны": "https://youtu.be/3VcKaXpzqRo",
    "разводка в наклоне": "https://youtu.be/EA7u4Q_8HQ0",
    "тяга к подбородку": "https://youtu.be/jaOXEMGMPZk",
    "махи гантелями вперёд": "https://youtu.be/1L_h6Ja3RPc",
    "подъём штанги на бицепс": "https://youtu.be/ykJmrZ5v0Oo",
    "подъём гантелей на бицепс": "https://youtu.be/sAq_ocpRh_I",
    "молотки": "https://youtu.be/zC3nLlEvin4",
    "концентрированный подъём": "https://youtu.be/Jvj2wV0vOFU",
    "жим узким хватом": "https://youtu.be/nEF0bv2FW94",
    "французский жим": "https://youtu.be/d_KZxkY_0cM",
    "разгибание на блоке": "https://youtu.be/kiuVA0gs3EI",
    "разгибание гантели": "https://youtu.be/YbX7Wd8jQ-U",
    "приседания со штангой": "https://youtu.be/Dy28eq2PjcM",
    "приседания": "https://youtu.be/aclHkVaku9U",
    "жим ногами": "https://youtu.be/IZxyjW7MPJQ",
    "выпады": "https://youtu.be/D7KaRcUTQeE",
    "румынская тяга": "https://youtu.be/JCXUYuzwNrM",
    "мёртвая тяга": "https://youtu.be/op9kVnSso6Q",
    "сгибание ног": "https://youtu.be/ELOCsoDSmrg",
    "разгибание ног": "https://youtu.be/YyvSfVjQeL0",
    "болгарский присед": "https://youtu.be/2C-uNgKwPLE",
    "икры стоя": "https://youtu.be/c_Dq_NCzj8M",
    "икры сидя": "https://youtu.be/JbyjNymZOt0",
    "ягодичный мостик": "https://youtu.be/OUgsJ8-Vi0E",
    "отведение ноги назад": "https://youtu.be/9kdVMVaXQL0",
    "скручивания": "https://youtu.be/Xyd_fa5zoEU",
    "планка": "https://youtu.be/pSHjTRCQxIw",
    "подъём ног лёжа": "https://youtu.be/JB2oyawG9KI",
    "русские скручивания": "https://youtu.be/wkD8rjkodUI",
    "велосипед": "https://youtu.be/1we3bh9yhqA",
    "подъём ног в висе": "https://youtu.be/hdng3Nm1x_E",
    "боковая планка": "https://youtu.be/K2VljzCC16g",
    "берпи": "https://youtu.be/dZgVxmf6jkA",
    "прыжки со скакалкой": "https://youtu.be/u3zgHI8QnqE",
    "бег на месте": "https://youtu.be/JWNw7bGKMEQ",
    "прыжки джек": "https://youtu.be/c4DAnQ6DtF8",
    "скалолаз": "https://youtu.be/nmwgirgXLYM",
    "становая тяга": "https://youtu.be/op9kVnSso6Q",
    "тяга сумо": "https://youtu.be/ej4rZFSXRCQ",
}


def _find_video(exercise_name: str) -> str:
    name_lower = exercise_name.lower().strip()
    if name_lower in EXERCISE_VIDEOS:
        return EXERCISE_VIDEOS[name_lower]
    for key, url in EXERCISE_VIDEOS.items():
        if key in name_lower or name_lower in key:
            return url
    keywords = name_lower.split()
    for key, url in EXERCISE_VIDEOS.items():
        if any(kw in key for kw in keywords if len(kw) > 4):
            return url
    return ""


def generate_monthly_plan(user_profile: dict) -> list:
    if not GEMINI_API_KEY:
        return _default_monthly_plan(user_profile)

    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    goal = user_profile.get("goal", "набор массы")
    experience = user_profile.get("experience", "начинающий")
    days_per_week = user_profile.get("days_per_week", 3)
    equipment = user_profile.get("equipment", "штанга, гантели")
    weight = user_profile.get("weight", 70)
    age = user_profile.get("age", 25)

    prompt = (
        "Ты профессиональный персональный тренер. Составь 30-дневный план тренировок.\n\n"
        f"ПРОФИЛЬ:\n"
        f"- Возраст: {age} лет\n"
        f"- Вес: {weight} кг\n"
        f"- Цель: {goal}\n"
        f"- Уровень: {experience}\n"
        f"- Тренировок в неделю: {days_per_week}\n"
        f"- Оборудование: {equipment}\n\n"
        "ТРЕБОВАНИЯ К ПЛАНУ:\n"
        f"1. Чередуй тренировочные дни с днями отдыха согласно {days_per_week} дням в неделю\n"
        "2. День отдыха = пустой массив []\n"
        "3. Каждый тренировочный день: 6-10 упражнений (полноценная тренировка!)\n"
        "4. Используй профессиональные сплиты:\n"
        "   - Набор массы: Push/Pull/Legs или Upper/Lower сплит\n"
        "   - Похудение: Full body + кардио элементы, круговые тренировки\n"
        "   - Рельеф: Комбо сплит с суперсетами, высокий объём\n"
        "   - Сила: 5x5 или линейная прогрессия\n"
        "5. Прогрессия нагрузки: каждую неделю увеличивай объём или интенсивность\n"
        "6. Включай базовые и изолирующие упражнения\n\n"
        "ФОРМАТ — верни ТОЛЬКО валидный JSON массив из ровно 30 элементов.\n"
        "Каждый элемент — массив упражнений или [] для дня отдыха.\n"
        "Каждое упражнение: {\"name\": string, \"sets\": int, \"reps\": string, \"rest\": int}\n"
        "Поле video_url НЕ включай.\n"
        "Верни ТОЛЬКО JSON без markdown, без пояснений."
    )

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```" in text:
            text = re.sub(r"```(?:json)?", "", text).strip()
        plan_raw = json.loads(text)
        while len(plan_raw) < 30:
            plan_raw.append([])
        plan_raw = plan_raw[:30]
        plan = []
        for day in plan_raw:
            if not day:
                plan.append([])
                continue
            enriched = []
            for ex in day:
                ex["video_url"] = _find_video(ex.get("name", ""))
                enriched.append(ex)
            plan.append(enriched)
        return plan
    except Exception as e:
        print(f"Gemini error: {e}")
        return _default_monthly_plan(user_profile)


def get_ai_motivation(exercise_name: str, sets_done: int, total_sets: int) -> str:
    if not GEMINI_API_KEY:
        return _default_motivation(sets_done, total_sets)
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
            f"Ты тренер. Пользователь выполнил {sets_done} из {total_sets} подходов "
            f"упражнения '{exercise_name}'. Напиши короткое мотивационное сообщение "
            "(1-2 предложения, без эмодзи)."
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return _default_motivation(sets_done, total_sets)


def _default_motivation(sets_done: int, total_sets: int) -> str:
    remaining = total_sets - sets_done
    if remaining == 0:
        return "Отличная работа! Упражнение выполнено!"
    elif remaining == 1:
        return "Последний подход! Выложись на максимум!"
    else:
        return f"Хорошо! Ещё {remaining} подхода — ты справишься!"


def _default_monthly_plan(user_profile: dict) -> list:
    days_per_week = user_profile.get("days_per_week", 3)
    full_body_day = [
        {"name": "Приседания", "sets": 4, "reps": "10-12", "rest": 90, "video_url": _find_video("приседания")},
        {"name": "Жим штанги лёжа", "sets": 4, "reps": "8-10", "rest": 90, "video_url": _find_video("жим штанги лёжа")},
        {"name": "Тяга штанги в наклоне", "sets": 4, "reps": "10", "rest": 90, "video_url": _find_video("тяга штанги в наклоне")},
        {"name": "Жим гантелей сидя", "sets": 3, "reps": "12", "rest": 60, "video_url": _find_video("жим гантелей сидя")},
        {"name": "Подъём штанги на бицепс", "sets": 3, "reps": "12", "rest": 60, "video_url": _find_video("подъём штанги на бицепс")},
        {"name": "Разгибание на блоке", "sets": 3, "reps": "12", "rest": 60, "video_url": _find_video("разгибание на блоке")},
        {"name": "Планка", "sets": 3, "reps": "60 сек", "rest": 45, "video_url": _find_video("планка")},
    ]
    plan = []
    for i in range(30):
        week_day = i % 7
        if week_day < days_per_week:
            plan.append(full_body_day)
        else:
            plan.append([])
    return plan
