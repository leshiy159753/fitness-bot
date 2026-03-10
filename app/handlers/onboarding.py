from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app.states import OnboardingStates
from app.database import save_user
from app.ai_service import generate_monthly_plan
from app.keyboards import (
    goals_keyboard, experience_keyboard, main_menu_keyboard,
    cancel_keyboard, GOAL_LABELS, EXP_LABELS
)

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    await state.set_state(OnboardingStates.name)
    await message.answer(
        "Отлично! Давай составим твой профиль \U0001f4aa\n\nКак тебя зовут?",
        reply_markup=cancel_keyboard()
    )


@router.message(OnboardingStates.name)
async def process_name(message: Message, state: FSMContext):
    if message.text == "\u274c Отмена":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu_keyboard())
        return
    await state.update_data(name=message.text)
    await state.set_state(OnboardingStates.age)
    await message.answer(f"Приятно познакомиться, {message.text}! Сколько тебе лет?")


@router.message(OnboardingStates.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (10 <= int(message.text) <= 100):
        await message.answer("Введи корректный возраст (10-100):")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(OnboardingStates.weight)
    await message.answer("Твой текущий вес (кг)?")


@router.message(OnboardingStates.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
        if not (30 <= weight <= 300):
            raise ValueError
    except ValueError:
        await message.answer("Введи корректный вес (30-300 кг):")
        return
    await state.update_data(weight=weight)
    await state.set_state(OnboardingStates.height)
    await message.answer("Твой рост (см)?")


@router.message(OnboardingStates.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = int(message.text)
        if not (100 <= height <= 250):
            raise ValueError
    except ValueError:
        await message.answer("Введи корректный рост (100-250 см):")
        return
    await state.update_data(height=height)
    await state.set_state(OnboardingStates.goal)
    await message.answer("Какая у тебя цель?", reply_markup=goals_keyboard())


@router.callback_query(OnboardingStates.goal, F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    goal_label = GOAL_LABELS.get(callback.data, callback.data)
    await state.update_data(goal=goal_label.split(" ", 1)[1])
    await state.set_state(OnboardingStates.experience)
    await callback.message.edit_text(
        "Какой у тебя уровень подготовки?",
        reply_markup=experience_keyboard()
    )
    await callback.answer()


@router.callback_query(OnboardingStates.experience, F.data.startswith("exp_"))
async def process_experience(callback: CallbackQuery, state: FSMContext):
    exp_label = EXP_LABELS.get(callback.data, callback.data)
    await state.update_data(experience=exp_label.split(" ", 1)[1])
    await state.set_state(OnboardingStates.days_per_week)
    await callback.message.edit_text("Сколько дней в неделю планируешь тренироваться? (1-7)")
    await callback.answer()


@router.message(OnboardingStates.days_per_week)
async def process_days(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (1 <= int(message.text) <= 7):
        await message.answer("Введи число от 1 до 7:")
        return
    await state.update_data(days_per_week=int(message.text))
    await state.set_state(OnboardingStates.equipment)
    await message.answer(
        "Какое оборудование доступно?\n"
        "(например: штанга, гантели, тренажёры / только своё тело)"
    )


@router.message(OnboardingStates.equipment)
async def process_equipment(message: Message, state: FSMContext):
    await state.update_data(equipment=message.text)
    data = await state.get_data()
    await state.clear()

    save_user(message.from_user.id, data)

    await message.answer(
        "\u23f3 Генерирую твой план тренировок на 30 дней...",
        reply_markup=main_menu_keyboard()
    )

    monthly_plan = generate_monthly_plan(data)
    save_user(message.from_user.id, {
        "monthly_plan": monthly_plan,
        "current_day": 0,
        "current_exercise_idx": 0,
        "today_sets": [],
    })

    # Count workout days
    workout_days = sum(1 for day in monthly_plan if day)

    await message.answer(
        f"\u2705 Профиль создан! План на 30 дней готов.\n\n"
        f"\U0001f4c5 Тренировочных дней: {workout_days}\n"
        f"\U0001f3af Цель: {data.get('goal')}\n"
        f"\U0001f4aa Уровень: {data.get('experience')}\n\n"
        f"Нажми *«\U0001f4c5 Тренировка сегодня»* чтобы начать!",
        parse_mode="Markdown"
    )
