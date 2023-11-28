from sqlalchemy import select
from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery
from bot.loader import bot, stadium_sts, manage_sts
from database import Stadium, Session
from .markups.buttons import *
from .markups.inline_buttons import *


@bot.message_handler(regexp="🛠️Stadionlarimni boshqarish", state=stadium_sts.init)
async def manage_stadium_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    markup = None
    async with bot.retrieve_data(user_id, chat_id) as data:
        stadiums_query = select(Stadium).where(Stadium.user_id == data["user_id"])
    async with Session.begin() as db:
        stadiums = (await db.execute(stadiums_query)).scalars()
        stadiums.all()
    await bot.send_message(chat_id, "Stadionni tanlang", reply_markup=markup)
    await bot.set_state(user_id, manage_sts.choose_stadium, chat_id)


@bot.callback_query_handler(func=lambda call: call, state=manage_sts.choose_stadium)
async def stadium_to_manage(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

