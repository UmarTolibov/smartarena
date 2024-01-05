from telebot.asyncio_handler_backends import State, StatesGroup


class Auth(StatesGroup):
    init = State()
    account = State()
    name = State()
    number = State()
    type = State()
    password = State()
    confirm = State()
    username = State()
    login_password = State()


class NeutralState():
    init = State()


class UserState(StatesGroup):
    init = State()
    main = State()
    region = State()
    district = State()
    date = State()
    start_time = State()
    hour = State()
    preview = State()
    loc_book = State()


class SuperUserState(StatesGroup):
    init = State()
    menu = State()


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


class ManageStadiums(StatesGroup):
    choose_stadium = State()
    edit = State()
    name = State()
    description = State()
    image = State()
    price = State()
    open_time = State()
    close_time = State()
    region = State()
    district = State()
    location = State()


class MyBookings(StatesGroup):
    init = State()


class Settings(StatesGroup):
    init = State()
    username = State()
    old_password = State()
    new_password = State()
    number = State()


class Help(StatesGroup):
    init = State()


class Book(StatesGroup):
    init = State()
