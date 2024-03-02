from telebot.types import Message
from bot.loader import bot, user_sts
from .markups.buttons import *


@bot.message_handler(regexp="🔙Bosh sahifa", state="*", is_admin=False, is_owner=False)
async def back_to_main(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Bosh sahifa:", reply_markup=main_menu_markup())
    await bot.set_state(user_id, user_sts.main, chat_id)


@bot.message_handler(regexp="🔙Orqaga", state="*", is_admin=False, is_owner=False)
async def back(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    state = await bot.get_state(user_id, chat_id)
    await bot.send_message(chat_id, "Bosh sahifa", reply_markup=main_menu_markup())
    await bot.set_state(user_id, user_sts.main, chat_id)
