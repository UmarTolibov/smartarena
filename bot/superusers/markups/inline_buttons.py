from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def accounts_inline(accounts):
    markup = InlineKeyboardMarkup()
    row_buttons = []
    for username, user_id in accounts:
        row_buttons.append(InlineKeyboardButton(username, callback_data=f"account|{user_id}"))
        if len(row_buttons) == 2:
            markup.row(*row_buttons)
            row_buttons = []
    return markup
