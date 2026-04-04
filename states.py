from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    waiting_for_pickup_station = State()
    waiting_for_payment_method = State()
