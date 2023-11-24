from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from bot.common.bot_config import __


def main_menu(lang):
    mark_up = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    book = KeyboardButton(__("book_stadium", lang) + "⛳️")
    view = KeyboardButton(__("view_bookings", lang) + "🏘")
    settings = KeyboardButton(__("account_settings", lang) + "⚙️")
    yours = KeyboardButton(__("your_stadiums", lang) + "⚙️")
    help_ = KeyboardButton(__("help", lang) + "ℹ️")
    mark_up.add(book, view, yours, settings, help_)
    return mark_up


def settings_menu(lang):
    mark_up = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    change_lang = KeyboardButton(__('change_lang', lang) + "🌐")
    username = KeyboardButton(__("update_username", lang) + "✏️")
    password = KeyboardButton(__("update_password", lang) + "🔐")
    email = KeyboardButton(__("update_email", lang) + "📧")
    number = KeyboardButton(__("update_number", lang) + "☎️")

    mark_up.add(username, password, email, number)
    return mark_up


def your_stadiums_menu(lang):
    mark_up = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    add_stadium = KeyboardButton(__("add_new_stadium", lang) + "🌐")
    manage_stadium = KeyboardButton(__("manage_stadiums", lang) + "🛠️")
    back = KeyboardButton(__("back", lang) + "🔙")

    mark_up.add(add_stadium, manage_stadium, back)
    return mark_up


def settings_default(lang='en'):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    change_lang = KeyboardButton(__('change_lang', lang) + "🌐")
    edit_user_info = KeyboardButton(__('edit_user', lang) + "✏️")
    back = KeyboardButton(__('back', lang) + "↪️")
    markup.add(change_lang, edit_user_info, back)
    return markup


async def products(category, lang):
    mark_up = ReplyKeyboardMarkup()


def back_basket(lang: str = 'en', basket: bool = True):
    mark_up = ReplyKeyboardMarkup(resize_keyboard=True)
    back = KeyboardButton(__('back', lang) + "↪️")
    basket_btn = KeyboardButton(__('basket', lang) + "📦")
    if basket:
        mark_up.add(back, basket_btn)
    else:
        mark_up.add(back)
    return mark_up


def registrate():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Sign up📝"), KeyboardButton("Log in📥"))


async def users_list_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(__('list', lang) + "🗒"))
    return markup


def lang_keyboard(back=False, lang='en'):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    uz = KeyboardButton('uz🇺🇿')
    ru = KeyboardButton('ru🇷🇺')
    en = KeyboardButton('en🇺🇸')
    back = KeyboardButton(__('back', lang) + "↪️")
    if back:
        markup.add(uz, ru, en)
        markup.add(back)
    else:
        markup.add(uz, ru, en)
    return markup


def contact_number_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    contact = KeyboardButton(__('share_contact', lang), request_contact=True)
    markup.add(contact)
    return markup


def gender_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    male = KeyboardButton(__('male', lang) + '🧔')
    female = KeyboardButton(__('female', lang) + '👩')
    markup.add(male, female)
    return markup


def login():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    log_in = KeyboardButton("Log in📥")
    markup.add(log_in)
    return markup


def cancel():
    return ReplyKeyboardMarkup(True).add(KeyboardButton("Cancel❌"))


def menu():
    lst = ["Add Stadium", "Get Stadium", "All Stadiums", "Add Order", "Get Order",
           "All Orders"]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(*[KeyboardButton(i) for i in lst[:3]])
    markup.row(*[KeyboardButton(i) for i in lst[3:6]])
    return markup
