from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def login_signup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Kirish↙️"), KeyboardButton("Ro\'yxatdan o\'tish🗒"))
    return markup


def number_request():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Kantaktni yuborish☎️", request_contact=True))
    return markup
