from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def login_signup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Kirish↙️"), KeyboardButton("Ro\'yxatdan o\'tish🗒"))
    return markup


def number_request():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Kantaktni yuborish☎️", request_contact=True))
    return markup


def main_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📆Bron qilish "), KeyboardButton("📅 Buyurtmalarni Ko'rish"))
    markup.row(KeyboardButton("🏟️Stadionlarim"), KeyboardButton("⚙️Sozlanmalar"))
    markup.row(KeyboardButton("ℹ️Yordam"))
    return markup


def view_bookings_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🔜 Kelayotgan buyurtmalar"), KeyboardButton("📆 Buyurtmalar tarixi"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup


def account_settings_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("✏️Username"), KeyboardButton("✏️Password"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup


def your_stadiums_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🌐Stadion qo'shish"), KeyboardButton("🛠️Stadionlarimni boshqarish"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup


def back():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🔙Orqaga"))
    markup.row(KeyboardButton("🔙Bosh sahifa"))
    return markup


def done():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Jo'natib bo'ldim👌"))
    return markup


def request_location():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Lokatsiyani jo'natish🗺📍", request_location=True))
    return markup
