from sqlalchemy import select
from telebot.types import Message
from bot.loader import bot, booking_sts
from database import Stadium, Order, Session
from .markups.buttons import *
from .markups.inline_buttons import *


# regexp="📅 Buyurtmalarni Ko'rish"
async def my_booking_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Buyurtmalarni ko'rish:", reply_markup=view_bookings_markup())
    await bot.set_state(user_id, booking_sts.init, chat_id)


# regexp="🔜 Kelayotgan buyurtmalar", state=booking_sts.init
async def upcoming_bookings(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    today = datetime.datetime.now()
    async with bot.retrieve_data(user_id, chat_id) as data:
        upcoming_orders_query = (
            select(Order.start_time, Order.hour, Stadium.name)
            .join(Stadium, Order.stadium_id == Stadium.id)
            .filter(Order.user_id == data["user_id"])
            .filter(Order.start_time >= today)
        )
    async with Session.begin() as db:
        result = (await db.execute(upcoming_orders_query)).all()
        text = ""

        for i in result:
            time = i[0].strftime("%y-%b %d.%H")
            text += f"""<b>Stadium</b>: {i[2]}
<b>Boshlanish sana/vaqti</b>: <code>{time}</code>
<b>Soat</b>: <code>{i[1]}</code>

"""

    if text == "":
        await bot.send_message(chat_id, "Buyurtmalar yo'q")
    else:
        await bot.send_message(chat_id, text, parse_mode="html", reply_markup=view_bookings_markup())
    await bot.set_state(user_id, booking_sts.init, chat_id)


# regexp="📆 Buyurtmalar tarixi", state=booking_sts.init
async def booking_history(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    today = datetime.datetime.now()
    async with bot.retrieve_data(user_id, chat_id) as data:
        orders_history_query = (
            select(Order.start_time, Order.hour, Stadium.name)
            .join(Stadium, Order.stadium_id == Stadium.id)
            .filter(Order.user_id == data["user_id"])
            .filter(Order.start_time <= today)
        )
    async with Session.begin() as db:
        result = (await db.execute(orders_history_query)).all()
        text = "Buyurtmalar tarixi Tarix"
        for i in result:
            time = i[0].strftime("%y-%b %d.%H")
            text += f"""<b>Stadium</b>: {i[2]}
<b>Boshlanish sana/vaqti</b>: <code>{time}</code>
<b>Soat</b>: <code>{i[1]}</code>

"""
    if text == "":
        await bot.send_message(chat_id, "Buyurtmalar yo'q")
    else:
        await bot.send_message(chat_id, text, parse_mode="html", reply_markup=view_bookings_markup())

    await bot.set_state(user_id, booking_sts.init, chat_id)
