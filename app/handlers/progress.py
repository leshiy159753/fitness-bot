from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.database import get_user, get_workout_history
from app.keyboards import main_menu_keyboard

router = Router()

@router.message(Command("progress"))
@router.message(F.text == "📊 Прогресс")
async def show_progress(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай профиль: /profile")
        return
    
    history = get_workout_history(message.from_user.id, limit=10)
    
    text = (
        f"📊 *Твой прогресс*\n\n"
        f"👤 {user.get('name')} | {user.get('age')} лет\n"
        f"⚖️ Вес: {user.get('weight')} кг | Рост: {user.get('height')} см\n"
        f"🎯 Цель: {user.get('goal')}\n"
        f"🏋️ Уровень: {user.get('experience')}\n"
        f"📅 Тренировок в неделю: {user.get('days_per_week')}\n\n"
    )
    
    if history:
        text += f"*Последние тренировки ({len(history)}):*\n"
        for entry in reversed(history):
            w = f" | {entry['weight']} кг" if entry.get('weight') else ""
            text += f"• {entry['date']} — {entry['exercise']} {entry['sets']}×{entry['reps']}{w}\n"
    else:
        text += "_Тренировок пока нет. Записывай через /log_"
    
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
