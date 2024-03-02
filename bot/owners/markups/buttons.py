from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📆Bron qilish"), KeyboardButton("📅 Buyurtmalarni Ko'rish"))
    markup.row(KeyboardButton("🏟️Stadionlarim"), KeyboardButton("⚙️Sozlanmalar"))
    return markup


def your_stadiums_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🌐Stadion qo'shish"), KeyboardButton("🛠️Stadionlarimni boshqarish"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup


def back():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton("🔙Orqaga"), KeyboardButton("🔙Bosh sahifa"))
    return markup


def done():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Jo'natib bo'ldim👌"))
    return markup


def request_location():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Lokatsiyani jo'natish🗺📍", request_location=True))
    return markup


def account_settings_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("✏️Username"), KeyboardButton("✏️Password"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup


def login_signup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Kirish↙️"), KeyboardButton("Ro\'yxatdan o\'tish🗒"))
    return markup
