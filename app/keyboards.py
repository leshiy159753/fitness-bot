from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="\U0001f4c5 Тренировка сегодня"),
        KeyboardButton(text="\U0001f4d4 Дневник тренировок")
    )
    builder.row(
        KeyboardButton(text="\U0001f4ca Прогресс"),
        KeyboardButton(text="\u2699\ufe0f Настройки")
    )
    return builder.as_markup(resize_keyboard=True)


def start_workout_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="\U0001f4aa Начать тренировку"))
    builder.row(KeyboardButton(text="\U0001f519 Главное меню"))
    return builder.as_markup(resize_keyboard=True)


def set_done_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="\u2705 Подход выполнен"),
        KeyboardButton(text="\u23ed Пропустить упражнение")
    )
    return builder.as_markup(resize_keyboard=True)


def exercise_done_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="\u27a1\ufe0f Следующее упражнение"))
    return builder.as_markup(resize_keyboard=True)


def finish_workout_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="\U0001f3c1 Завершить тренировку"))
    return builder.as_markup(resize_keyboard=True)


def goals_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="\U0001f525 Похудение", callback_data="goal_weight_loss"))
    builder.row(InlineKeyboardButton(text="\U0001f4aa Набор массы", callback_data="goal_muscle_gain"))
    builder.row(InlineKeyboardButton(text="\u2696\ufe0f Поддержание формы", callback_data="goal_maintenance"))
    builder.row(InlineKeyboardButton(text="\U0001f3cb\ufe0f Сила", callback_data="goal_strength"))
    return builder.as_markup()


def experience_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="\U0001f331 Новичок", callback_data="exp_beginner"))
    builder.row(InlineKeyboardButton(text="\U0001f3cb\ufe0f Средний", callback_data="exp_intermediate"))
    builder.row(InlineKeyboardButton(text="\U0001f3c6 Продвинутый", callback_data="exp_advanced"))
    return builder.as_markup()


def settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="\u2696\ufe0f Обновить вес", callback_data="settings_weight"))
    builder.row(InlineKeyboardButton(text="\U0001f3af Изменить цель", callback_data="settings_goal"))
    builder.row(InlineKeyboardButton(text="\U0001f464 Мой профиль", callback_data="settings_profile"))
    return builder.as_markup()


def cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="\u274c Отмена"))
    return builder.as_markup(resize_keyboard=True)


GOAL_LABELS = {
    "goal_weight_loss": "\U0001f525 Похудение",
    "goal_muscle_gain": "\U0001f4aa Набор массы",
    "goal_maintenance": "\u2696\ufe0f Поддержание формы",
    "goal_strength": "\U0001f3cb\ufe0f Сила",
}

EXP_LABELS = {
    "exp_beginner": "\U0001f331 Новичок",
    "exp_intermediate": "\U0001f3cb\ufe0f Средний",
    "exp_advanced": "\U0001f3c6 Продвинутый",
}
