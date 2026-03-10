from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app.database import get_user, save_user
from app.keyboards import settings_keyboard, main_menu_keyboard, goals_keyboard, cancel_keyboard, GOAL_LABELS
from app.states import SettingsStates
from app.ai_service import generate_monthly_plan

router = Router()

@router.message(Command("settings"))
@router.message(F.text == "\u2699\ufe0f Настройки")
async def show_settings(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай профиль: /profile")
        return
    await message.answer("\u2699\ufe0f Настройки:", reply_markup=settings_keyboard())

@router.callback_query(F.data == "settings_weight")
async def edit_weight(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.editing_weight)
    await callback.message.answer("Введи новый вес (кг):", reply_markup=cancel_keyboard())
    await callback.answer()

@router.message(SettingsStates.editing_weight)
async def save_weight(message: Message, state: FSMContext):
    if message.text == "\u274c Отмена":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu_keyboard())
        return
    try:
        weight = float(message.text.replace(",", "."))
        if not (30 <= weight <= 300):
            raise ValueError
    except ValueError:
        await message.answer("Введи корректный вес (30-300 кг):")
        return
    save_user(message.from_user.id, {"weight": weight})
    await state.clear()
    await message.answer(f"\u2705 Вес обновлён: {weight} кг", reply_markup=main_menu_keyboard())

@router.callback_query(F.data == "settings_goal")
async def edit_goal(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.editing_goal)
    await callback.message.answer("Выбери новую цель:", reply_markup=goals_keyboard())
    await callback.answer()

@router.callback_query(SettingsStates.editing_goal, F.data.startswith("goal_"))
async def save_goal(callback: CallbackQuery, state: FSMContext):
    goal_label = GOAL_LABELS.get(callback.data, callback.data)
    goal = goal_label.split(" ", 1)[1]
    save_user(callback.from_user.id, {"goal": goal})
    await state.clear()

    user = get_user(callback.from_user.id)
    await callback.message.answer(
        "\u23f3 Цель обновлена. Перегенерирую план...",
        reply_markup=main_menu_keyboard()
    )

    monthly_plan = generate_monthly_plan(user)
    save_user(callback.from_user.id, {
        "monthly_plan": monthly_plan,
        "current_day": 0,
        "current_exercise_idx": 0,
        "today_sets": [],
    })

    workout_days = sum(1 for day in monthly_plan if day)
    await callback.message.answer(
        f"\u2705 Цель обновлена: {goal_label}\n\n"
        f"\U0001f4c5 Новый план готов: {workout_days} тренировочных дней из 30.",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "settings_profile")
async def show_profile(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден")
        return
    text = (
        f"\U0001f464 *Профиль*\n\n"
        f"Имя: {user.get('name')}\n"
        f"Возраст: {user.get('age')} лет\n"
        f"Вес: {user.get('weight')} кг\n"
        f"Рост: {user.get('height')} см\n"
        f"Цель: {user.get('goal')}\n"
        f"Уровень: {user.get('experience')}\n"
        f"Дней/неделю: {user.get('days_per_week')}\n"
        f"Оборудование: {user.get('equipment')}\n"
        f"\U0001f4c5 Текущий день: {user.get('current_day', 0) + 1}/30"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()
