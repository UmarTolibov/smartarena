from telebot.asyncio_handler_backends import State, StatesGroup


class Auth(StatesGroup):
    init = State()
    account = State()
    name = State()
    number = State()
    password = State()
    confirm = State()
    username = State()
    login_password = State()


class UserState(StatesGroup):
    main = State()
    region = State()


class StadiumState(StatesGroup):
    init = State()
    name = State()
    description = State()
    image = State()
    price = State()
    open_time = State()
    close_time = State()
    region = State()
    district = State()
    location = State()
    confirm = State()
