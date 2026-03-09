from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.database import get_user
from app.keyboards import main_menu_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = get_user(message.from_user.id)
    if user:
        await message.answer(
            f"С возвращением, {user.get('name', 'спортсмен')}! 💪\n\nЧем займёмся сегодня?",
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer(
            "Привет! Я твой персональный фитнес-тренер 🏋️\n\n"
            "Составлю программу тренировок под твои цели и помогу вести дневник.\n\n"
            "Напиши /profile чтобы начать настройку профиля!"
        )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 *Доступные команды:*\n\n"
        "/start — Начало работы\n"
        "/profile — Настроить профиль\n"
        "/program — Моя программа тренировок\n"
        "/log — Записать тренировку\n"
        "/progress — Мой прогресс\n"
        "/menu — Главное меню",
        parse_mode="Markdown"
    )
