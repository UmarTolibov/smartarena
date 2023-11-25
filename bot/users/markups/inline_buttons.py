from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def confirmation():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Tasdiqlash✅", callback_data="confirm"))
    markup.row(InlineKeyboardButton("O\'zgartirish✏️", callback_data="reject"))
    return markup
