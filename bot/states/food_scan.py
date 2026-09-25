from aiogram.fsm.state import State, StatesGroup

class FoodScanStates(StatesGroup):
    """Состояния для сканирования еды"""
    waiting_for_photo = State()
    confirming_results = State()
    adjusting_portions = State()
