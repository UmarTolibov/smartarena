from telebot.types import Message
from bot.loader import bot, auth_sts
from .markups.buttons import login_signup


@bot.message_handler(commands=["start"])
async def greeting(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    markup = login_signup()
    print(message.date)
    await bot.send_message(chat_id, f"Salom {message.from_user.first_name}", reply_to_message_id=message.message_id,
                           reply_markup=markup)
    await bot.set_state(user_id, auth_sts.init, chat_id)