from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.common.bot_config import __


async def product_detail_markup(category_id: int, product_id: int, p_page: int = 0, quantity: int = 1, lang='en'):
    mark_up = InlineKeyboardMarkup(keyboard=[
        [InlineKeyboardButton('-', callback_data=f'minus|{quantity}'),
         InlineKeyboardButton(f'{quantity}', callback_data=f'quantity|{quantity}'),
         InlineKeyboardButton('+', callback_data=f'plus|{quantity}')
         ],
        [
            # InlineKeyboardButton('⏪', callback_data=f'prev|{p_page}'),
            InlineKeyboardButton(__('add', lang) + "📦", callback_data=f'add|{product_id}')
            # InlineKeyboardButton('⏩', callback_data=f'next|{p_page}')
        ]
    ])
    return mark_up


async def basket_inline(products: tuple, total: int, lang: str):
    mark_up = InlineKeyboardMarkup(keyboard=[
        [InlineKeyboardButton('-', callback_data=f'less|{i[0]}|{i[1]}|{i[2]}'),
         InlineKeyboardButton(f'{i[0]}', callback_data=f'basket_product|{i[0]}|{i[1]}|{i[2]}'),
         InlineKeyboardButton('+', callback_data=f'more|{i[0]}|{i[1]}|{i[2]}')]
        for i in products if i[1] > 0])
    # i[0] product title
    # i[1] product quantity
    mark_up.row(InlineKeyboardButton(__('buy', lang) + "💳", callback_data=f'buy_get|{total}'),
                InlineKeyboardButton(__('clear_basket', lang) + "🗑", callback_data=f'clear'))
    mark_up.row(InlineKeyboardButton(__('continue_shopping', lang) + "🛍", callback_data=f'continue_shopping'))
    return mark_up if len(mark_up.keyboard) > 2 else None


def confirmation_inline(lang='en', confirm=True):
    markup = InlineKeyboardMarkup()
    name = InlineKeyboardButton(f'{__("btn_name", lang)}✏️', callback_data='edit_name')
    gender = InlineKeyboardButton(f'{__("btn_gender", lang)}✏️', callback_data='edit_gender')
    email = InlineKeyboardButton(f'{__("btn_email", lang)}✏️', callback_data='edit_email')
    number = InlineKeyboardButton(f'{__("btn_number", lang)}✏️', callback_data='edit_number')
    confirm = InlineKeyboardButton(f'{__("btn_confirm", lang)}✅', callback_data='confirm')
    markup.row(name, email)
    markup.row(number, gender)
    if confirm:
        markup.row(confirm)
    return markup


def crud_markup(data_id: int, order=False):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(InlineKeyboardButton("Edit✏️", callback_data=f"s_edit|{data_id}" if not order else f"o_edit|{data_id}"),
               InlineKeyboardButton("Delete⛔️",
                                    callback_data=f"s_delete|{data_id}" if not order else f"o_delete|{data_id}"))
    return markup
