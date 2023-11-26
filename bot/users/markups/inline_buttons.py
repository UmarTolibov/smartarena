from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def confirmation():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Tasdiqlash✅", callback_data="confirm"))
    markup.add(InlineKeyboardButton("O\'zgartirish✏️", callback_data="reject"))
    return markup
