from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.database import get_user, get_workout_history
from app.keyboards import main_menu_keyboard

router = Router()

@router.message(Command("progress"))
@router.message(F.text == "\U0001f4ca Прогресс")
async def show_progress(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай профиль: /profile")
        return

    history = get_workout_history(message.from_user.id, limit=10)
    plan = user.get("monthly_plan", [])
    current_day = user.get("current_day", 0)
    workout_days_total = sum(1 for day in plan if day)
    workout_days_done = sum(
        1 for day in plan[:current_day] if day
    )

    text = (
        f"\U0001f4ca *Твой прогресс*\n\n"
        f"\U0001f464 {user.get('name')} | {user.get('age')} лет\n"
        f"\u2696\ufe0f Вес: {user.get('weight')} кг | Рост: {user.get('height')} см\n"
        f"\U0001f3af Цель: {user.get('goal')}\n"
        f"\U0001f3cb\ufe0f Уровень: {user.get('experience')}\n\n"
        f"\U0001f4c5 *План на 30 дней:*\n"
        f"День: {current_day + 1}/30\n"
        f"Тренировок выполнено: {workout_days_done}/{workout_days_total}\n\n"
    )

    if history:
        text += f"*Последние упражнения ({len(history)}):*\n"
        for entry in reversed(history):
            sets_info = ", ".join(
                f"{s['reps']} повт.{(' / ' + str(s['weight']) + ' кг') if s.get('weight') else ''}"
                for s in entry.get("sets", [])
            )
            text += f"\u2022 {entry['date']} — {entry['exercise']}\n  {sets_info}\n"
    else:
        text += "_Тренировок пока нет. Начни первую! \U0001f4aa_"

    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
