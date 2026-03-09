from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    name = State()
    age = State()
    weight = State()
    height = State()
    goal = State()
    experience = State()
    days_per_week = State()
    equipment = State()


class WorkoutStates(StatesGroup):
    logging_exercise = State()
    logging_sets = State()
    logging_weight = State()


class SettingsStates(StatesGroup):
    editing_weight = State()
    editing_goal = State()
