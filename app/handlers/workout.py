from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.database import get_user, log_workout
from app.keyboards import main_menu_keyboard, workout_log_keyboard
from app.states import WorkoutStates

router = Router()

@router.message(Command("program"))
@router.message(F.text == "💪 Моя программа")
async def show_program(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай профиль: /profile")
        return
    program = user.get("program", "Программа не создана. Перейди в /profile")
    await message.answer(program, parse_mode="Markdown")

@router.message(Command("log"))
@router.message(F.text == "📔 Дневник тренировок")
async def start_log(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала создай профиль: /profile")
        return
    await state.set_state(WorkoutStates.logging_exercise)
    await message.answer(
        "📝 Записываем тренировку!\n\nКакое упражнение выполнял?",
        reply_markup=workout_log_keyboard()
    )

@router.message(WorkoutStates.logging_exercise)
async def log_exercise(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu_keyboard())
        return
    await state.update_data(exercise=message.text)
    await state.set_state(WorkoutStates.logging_sets)
    await message.answer("Сколько подходов × повторений? (например: 3×10)")

@router.message(WorkoutStates.logging_sets)
async def log_sets(message: Message, state: FSMContext):
    parts = message.text.replace("х", "x").split("x")
    if len(parts) != 2 or not all(p.strip().isdigit() for p in parts):
        await message.answer("Введи в формате: 3×10 (подходы×повторения)")
        return
    sets, reps = int(parts[0].strip()), int(parts[1].strip())
    await state.update_data(sets=sets, reps=reps)
    await state.set_state(WorkoutStates.logging_weight)
    await message.answer("Вес (кг)? Если без веса — напиши 0")

@router.message(WorkoutStates.logging_weight)
async def log_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введи число (например: 60 или 0):")
        return
    data = await state.get_data()
    await state.clear()
    
    log_workout(
        message.from_user.id,
        data["exercise"],
        data["sets"],
        data["reps"],
        weight if weight > 0 else None
    )
    
    weight_str = f" | {weight} кг" if weight > 0 else ""
    await message.answer(
        f"✅ Записано!\n\n*{data['exercise']}* — {data['sets']}×{data['reps']}{weight_str}\n\nЗаписать ещё? /log",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
