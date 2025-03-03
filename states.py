from aiogram.fsm.state import State, StatesGroup

class AddProductStates(StatesGroup):
    waiting_for_url = State()