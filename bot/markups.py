from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def login():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    log_in = KeyboardButton("Login")
    markup.add(log_in)
    return markup


def crud_markup(data_id: int, order=False):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(InlineKeyboardButton("Edit✏️", callback_data=f"s_edit|{data_id}" if not order else f"o_edit|{data_id}"),
               InlineKeyboardButton("Delete⛔️",
                                    callback_data=f"s_delete|{data_id}" if not order else f"o_delete|{data_id}"))
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
