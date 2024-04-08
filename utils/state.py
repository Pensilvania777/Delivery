from aiogram.fsm.state import StatesGroup, State


class Delivery_add(StatesGroup):
    delivery_text = State()
    delivery_day = State()

class Cura_add(StatesGroup):
    cura_name = State()
    cura_external = State()

class Cura_tovar(StatesGroup):
    name_tovar = State()

class Admin(StatesGroup):
    admin_name = State()
    admin_id = State()

class Admin_cura(StatesGroup):
    cura_name = State()

class Tovar_cura(StatesGroup):
    tovar_cura = State()

class Edit_deliver(StatesGroup):
    month = State()
    day = State()
    number_delivery = State()
    adress_delivery = State()
    coll_tovar = State()
    name_tovar = State()
    price_shop = State()
    price_deliver = State()
    cash_card = State()
    name_cura = State()