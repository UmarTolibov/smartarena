from sqlalchemy import select
from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery, InputMediaPhoto
from bot.loader import bot, stadium_sts, manage_sts
from database import Stadium, Session
from .markups.buttons import *
from .markups.inline_buttons import *


@bot.message_handler(regexp="🛠️Stadionlarimni boshqarish", state=stadium_sts.init)
async def manage_stadium_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        stadiums_query = select(Stadium.name, Stadium.id).where(Stadium.user_id == data["user_id"])
    async with Session.begin() as db:
        stadiums = (await db.execute(stadiums_query)).fetchall()
        markup = stadiums_choose(stadiums)
    await bot.send_message(chat_id, "Stadionni tanlang", reply_markup=markup)
    await bot.set_state(user_id, manage_sts.choose_stadium, chat_id)


@bot.callback_query_handler(func=lambda call: "stadium" in call.data.split("|"), state=manage_sts.choose_stadium)
async def stadium_to_manage(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = int(call.data.split("|")[1])
    async with Session() as db:
        s_query = select(Stadium).where(Stadium.id == data)
        stadium = (await db.execute(s_query)).scalar()
        images = [InputMediaPhoto(i) for i in json.loads(stadium.image_urls)]
        markup = manage_stadium()
        message = f"""
<b>Nomi:</b> {stadium.name}
<b>Ma'lumot:</b> {stadium.description}
<b>Narxi:</b> {stadium.price} so'm/soat
<b>Ochilish vaqti:</b> {stadium.opening_time}
<b>Yopilish vaqti:</b> {stadium.closing_time}
<b>Viloyat:</b> {stadium.region}
<b>Tuman:</b> <i>{stadium.district}</i>"""
        await bot.send_location(chat_id, **stadium.location)
        await bot.send_media_group(chat_id, images)
        await bot.send_message(chat_id, message, parse_mode="html", reply_markup=markup)
