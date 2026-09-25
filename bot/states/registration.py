from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Пошаговое создание профиля пользователя."""
    phone = State()
    age = State()
    gender = State()
    height = State()
    current_weight = State()
    target_weight = State()
    activity_level = State()
    goal = State()
    experience_level = State()
    training_days = State()
    sleep_hours = State()
