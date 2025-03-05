from aiogram.fsm.state import StatesGroup, State, default_state


class New_Category(StatesGroup):
    cat_start   = State()
    cat_title   = State()


class Upd_Category(StatesGroup):
    new_title   = State()

class New_spend(StatesGroup):
    category    = State()
    amount      = State()
    desc        = State()

class Upd_spend(StatesGroup):
    amount      = State()
    desc        = State()
