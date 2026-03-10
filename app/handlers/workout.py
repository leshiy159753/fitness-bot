from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.database import (
    get_user, save_user, log_exercise_sets,
    advance_exercise, finish_day, get_workout_history
)
from app.keyboards import (
    main_menu_keyboard, start_workout_keyboard,
    set_done_keyboard, exercise_done_keyboard, finish_workout_keyboard
)
from app.states import WorkoutStates
from app.ai_service import get_ai_motivation

router = Router()


def _get_today_exercise(user: dict) -> dict | None:
    """Return current exercise dict or None if day is rest/done."""
    plan = user.get("monthly_plan", [])
    day_idx = user.get("current_day", 0)
    if not plan or day_idx >= len(plan):
        return None
    today = plan[day_idx]
    if not today:
        return None
    ex_idx = user.get("current_exercise_idx", 0)
    if ex_idx >= len(today):
        return None
    return today[ex_idx]


def _format_exercise_card(exercise: dict, ex_num: int, total: int, sets_done: int) -> str:
    """Format exercise info as a message."""
    video_line = f"\n\U0001f3a5 Видео: {exercise['video_url']}" if exercise.get("video_url") else ""
    return (
        f"*Упражнение {ex_num}/{total}*\n\n"
        f"\U0001f3cb\ufe0f *{exercise['name']}*\n"
        f"\U0001f4ca Подходов: {exercise['sets']} | Повторений: {exercise['reps']}\n"
        f"\u23f1 Отдых: {exercise['rest']} сек{video_line}\n\n"
        f"Выполнено подходов: {sets_done}/{exercise['sets']}\n\n"
        f"Введи результат в формате: *вес повторений*\n"
        f"Например: `80 10` (80 кг, 10 повторений)\n"
        f"Если без веса: `0 12`"
    )


@router.message(Command("today"))
@router.message(F.text == "\U0001f4c5 Тренировка сегодня")
async def show_today(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user or not user.get("monthly_plan"):
        await message.answer(
            "Сначала создай профиль и план: /profile",
            reply_markup=main_menu_keyboard()
        )
        return

    day_idx = user.get("current_day", 0)
    plan = user.get("monthly_plan", [])

    if day_idx >= len(plan):
        await message.answer(
            "\U0001f389 Ты завершил все 30 дней программы! Отличная работа!\n\n"
            "Создай новый план: /profile",
            reply_markup=main_menu_keyboard()
        )
        return

    today = plan[day_idx]
    if not today:
        await message.answer(
            f"\U0001f634 День {day_idx + 1} — день отдыха.\n\n"
            f"Восстанавливайся, следующая тренировка скоро!",
            reply_markup=main_menu_keyboard()
        )
        # Auto-advance rest day
        finish_day(message.from_user.id)
        return

    # Build today's exercise list
    lines = [f"\U0001f4c5 *День {day_idx + 1} из 30*\n"]
    for i, ex in enumerate(today, 1):
        lines.append(f"{i}. {ex['name']} — {ex['sets']}\u00d7{ex['reps']}")

    lines.append(f"\nВсего упражнений: {len(today)}")
    await message.answer(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=start_workout_keyboard()
    )


@router.message(F.text == "\U0001f4aa Начать тренировку")
async def start_workout(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай профиль: /profile")
        return

    # Reset exercise index to start from beginning
    save_user(message.from_user.id, {
        "current_exercise_idx": 0,
        "today_sets": [],
    })

    plan = user.get("monthly_plan", [])
    day_idx = user.get("current_day", 0)
    today = plan[day_idx] if plan and day_idx < len(plan) else []

    if not today:
        await message.answer("Сегодня день отдыха!", reply_markup=main_menu_keyboard())
        return

    exercise = today[0]
    text = _format_exercise_card(exercise, 1, len(today), 0)
    motivation = get_ai_motivation(exercise["name"], 0, exercise["sets"])

    await state.set_state(WorkoutStates.logging_set)
    await state.update_data(sets_done=0)
    await message.answer(
        f"{text}\n\n_{motivation}_",
        parse_mode="Markdown",
        reply_markup=set_done_keyboard()
    )


@router.message(WorkoutStates.logging_set)
async def log_set(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user:
        return

    # Handle skip
    if message.text == "\u23ed Пропустить упражнение":
        await _next_exercise(message, state, user, skipped=True)
        return

    # Handle "set done" button
    if message.text == "\u2705 Подход выполнен":
        state_data = await state.get_data()
        sets_done = state_data.get("sets_done", 0) + 1
        today_sets = user.get("today_sets", [])
        today_sets.append({"reps": "?", "weight": None})
        save_user(message.from_user.id, {"today_sets": today_sets})
        await state.update_data(sets_done=sets_done)
        await _after_set(message, state, user, sets_done)
        return

    # Parse "weight reps" input
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer(
            "Введи в формате: *вес повторений*\nНапример: `80 10` или `0 12`",
            parse_mode="Markdown"
        )
        return

    try:
        weight = float(parts[0].replace(",", "."))
        reps = int(parts[1])
    except ValueError:
        await message.answer(
            "Введи числа. Например: `80 10`",
            parse_mode="Markdown"
        )
        return

    # Save set
    today_sets = user.get("today_sets", [])
    today_sets.append({"reps": reps, "weight": weight if weight > 0 else None})
    save_user(message.from_user.id, {"today_sets": today_sets})

    state_data = await state.get_data()
    sets_done = state_data.get("sets_done", 0) + 1
    await state.update_data(sets_done=sets_done)

    weight_str = f"{weight} кг" if weight > 0 else "без веса"
    await message.answer(f"\u2705 Подход {sets_done}: {reps} повт., {weight_str}")

    await _after_set(message, state, user, sets_done)


async def _after_set(message: Message, state: FSMContext, user: dict, sets_done: int):
    """Check if exercise is done, prompt next set or next exercise."""
    exercise = _get_today_exercise(user)
    if not exercise:
        return

    plan = user.get("monthly_plan", [])
    day_idx = user.get("current_day", 0)
    today = plan[day_idx]
    total_exercises = len(today)

    if sets_done < exercise["sets"]:
        motivation = get_ai_motivation(exercise["name"], sets_done, exercise["sets"])
        await message.answer(
            f"\u23f1 Отдых {exercise['rest']} сек\n\n_{motivation}_\n\n"
            f"Подход {sets_done + 1}/{exercise['sets']}:",
            parse_mode="Markdown",
            reply_markup=set_done_keyboard()
        )
    else:
        ex_idx = user.get("current_exercise_idx", 0)
        log_exercise_sets(
            message.from_user.id,
            exercise["name"],
            user.get("today_sets", [])
        )
        save_user(message.from_user.id, {"today_sets": []})

        ex_num = ex_idx + 1
        if ex_num < total_exercises:
            await state.update_data(sets_done=0)
            await message.answer(
                f"\U0001f389 Упражнение завершено! ({ex_num}/{total_exercises})",
                reply_markup=exercise_done_keyboard()
            )
            await state.set_state(WorkoutStates.between_sets)
        else:
            await state.clear()
            finish_day(message.from_user.id)
            history = get_workout_history(message.from_user.id, limit=len(today))
            summary_lines = ["\U0001f3c1 *Тренировка завершена!*\n"]
            for entry in history[-len(today):]:
                sets_info = ", ".join(
                    f"{s['reps']} повт.{(' / ' + str(s['weight']) + ' кг') if s.get('weight') else ''}"
                    for s in entry["sets"]
                )
                summary_lines.append(f"\u2022 {entry['exercise']}: {sets_info}")
            summary_lines.append(f"\nОтличная работа! До следующей тренировки \U0001f4aa")
            await message.answer(
                "\n".join(summary_lines),
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard()
            )


@router.message(WorkoutStates.between_sets, F.text == "\u27a1\ufe0f Следующее упражнение")
async def next_exercise(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user:
        return
    await _next_exercise(message, state, user)


async def _next_exercise(message: Message, state: FSMContext, user: dict, skipped: bool = False):
    """Advance to next exercise or finish workout."""
    has_next = advance_exercise(message.from_user.id)
    user = get_user(message.from_user.id)

    plan = user.get("monthly_plan", [])
    day_idx = user.get("current_day", 0)
    today = plan[day_idx] if plan and day_idx < len(plan) else []
    total_exercises = len(today)

    if has_next:
        exercise = _get_today_exercise(user)
        ex_idx = user.get("current_exercise_idx", 0)
        text = _format_exercise_card(exercise, ex_idx + 1, total_exercises, 0)
        motivation = get_ai_motivation(exercise["name"], 0, exercise["sets"])
        prefix = "\u23ed Пропущено. " if skipped else ""
        await state.set_state(WorkoutStates.logging_set)
        await state.update_data(sets_done=0)
        await message.answer(
            f"{prefix}{text}\n\n_{motivation}_",
            parse_mode="Markdown",
            reply_markup=set_done_keyboard()
        )
    else:
        await state.clear()
        finish_day(message.from_user.id)
        await message.answer(
            "\U0001f3c1 *Тренировка завершена!* Отличная работа! \U0001f4aa",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )


@router.message(Command("history"))
@router.message(F.text == "\U0001f4d4 Дневник тренировок")
async def show_history(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай профиль: /profile")
        return

    history = get_workout_history(message.from_user.id, limit=10)
    if not history:
        await message.answer(
            "Дневник пуст. Проведи первую тренировку! \U0001f4aa",
            reply_markup=main_menu_keyboard()
        )
        return

    lines = ["\U0001f4d4 *Последние тренировки:*\n"]
    for entry in reversed(history):
        sets_info = ", ".join(
            f"{s['reps']} повт.{(' / ' + str(s['weight']) + ' кг') if s.get('weight') else ''}"
            for s in entry["sets"]
        )
        lines.append(f"*{entry['date']}* — {entry['exercise']}\n  {sets_info}")

    await message.answer(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
