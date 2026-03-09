from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="💪 Моя программа"),
        KeyboardButton(text="📔 Дневник тренировок")
    )
    builder.row(
        KeyboardButton(text="📊 Прогресс"),
        KeyboardButton(text="⚙️ Настройки")
    )
    return builder.as_markup(resize_keyboard=True)


def workout_log_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="✅ Выполнено"),
        KeyboardButton(text="⏭ Пропустить")
    )
    builder.row(KeyboardButton(text="🔙 Назад"))
    return builder.as_markup(resize_keyboard=True)


def goals_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔥 Похудение", callback_data="goal_weight_loss"))
    builder.row(InlineKeyboardButton(text="💪 Набор массы", callback_data="goal_muscle_gain"))
    builder.row(InlineKeyboardButton(text="⚖️ Поддержание формы", callback_data="goal_maintenance"))
    builder.row(InlineKeyboardButton(text="🛑 Сила", callback_data="goal_strength"))
    return builder.as_markup()


def experience_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🌱 Новичок", callback_data="exp_beginner"))
    builder.row(InlineKeyboardButton(text="🏋️ Средний", callback_data="exp_intermediate"))
    builder.row(InlineKeyboardButton(text="🏆 Продвинутый", callback_data="exp_advanced"))
    return builder.as_markup()


def settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⚖️ Обновить вес", callback_data="settings_weight"))
    builder.row(InlineKeyboardButton(text="🎯 Изменить цель", callback_data="settings_goal"))
    builder.row(InlineKeyboardButton(text="👤 Мой профиль", callback_data="settings_profile"))
    return builder.as_markup()


def cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)


GOAL_LABELS = {
    "goal_weight_loss": "🔥 Похудение",
    "goal_muscle_gain": "💪 Набор массы",
    "goal_maintenance": "⚖️ Поддержание формы",
    "goal_strength": "🛑 Сила",
}

EXP_LABELS = {
    "exp_beginner": "🌱 Новичок",
    "exp_intermediate": "🏋️ Средний",
    "exp_advanced": "🏆 Продвинутый",
}
