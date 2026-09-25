from aiogram.fsm.state import State, StatesGroup


class ProfileEditStates(StatesGroup):
    edit_age = State()
    edit_gender = State()
    edit_height = State()
    edit_current_weight = State()
    edit_target_weight = State()
    edit_activity_level = State()
    edit_goal = State()
    edit_experience_level = State()
    edit_training_days = State()
    edit_sleep_hours = State()
