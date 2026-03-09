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
    viewing_exercise = State()   # показываем упражнение с видео
    logging_set = State()        # ждём ввод "вес x повторений"
    between_sets = State()       # между подходами


class SettingsStates(StatesGroup):
    editing_weight = State()
    editing_goal = State()
