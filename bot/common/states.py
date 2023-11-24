from telebot.asyncio_handler_backends import State, StatesGroup


class RegistrationState(StatesGroup):
    register = State()
    lang = State()
    name = State()
    gender = State()
    email = State()
    number = State()
    date_birth = State()
    confirm = State()


class CustomState(StatesGroup):
    menu = State()
    main = State()
    log_in = State()
    username = State()
    password = State()
    get_stadium = State()
    get_order = State()
    get_stadium_json = State()
    get_order_json = State()

    edit = State()
    o_edit = State()
