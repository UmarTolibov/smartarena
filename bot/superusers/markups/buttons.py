from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📆Bron qilish "), KeyboardButton("📅 Buyurtmalarni Ko'rish"))
    markup.row(KeyboardButton("🏟️Stadionlarim"), KeyboardButton("⚙️Sozlanmalar"))
    markup.row(KeyboardButton("👨‍💻Admin"))
    return markup


def admin_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("Foydalanuvchilar👥"), KeyboardButton("Stadionlar🏟"))
    markup.row(KeyboardButton("Buyurtmalar🗒"), KeyboardButton("🔙Bosh sahifa"))
    return markup