from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot.loader import bot
from database import Stadium, Order, Session
from .markups.buttons import *
from .markups.inline_buttons import *


@bot.message_handler(regexp="📆Bron qilish")
async def book_stadium(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Viloyatni tanlang", reply_markup=regions_inline())


@bot.callback_query_handler(func=lambda call: "region" in call.data.split('|'))
async def region_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    region_id = int(call.data.split("|")[1])
    markup = district_inline(region_id)
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["region"] = region_id
        with open("bot/users/markups/regions.json", "r", encoding="utf-8") as file:
            region = json.load(file)["regions"][region_id - 1]
        data["region_name"] = region['name']
    sent = await bot.send_message(chat_id, f"{region['name']}", reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(chat_id, sent.message_id)
    await bot.edit_message_text("Tumanni tanlang", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "district" in call.data.split('|'))
async def district_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    district_id = int(call.data.split("|")[1])
    markup = start_time_inline()
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["district"] = district_id
        with open("bot/users/markups/regions.json", "r", encoding="utf-8") as file:
            district = json.load(file)["districts"][district_id - 15]
            data["district_name"] = district['name']
    await bot.edit_message_text("Boshlash vaqti", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "start_time" in call.data.split('|'))
async def start_time_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    start_time = call.data.split("|")[1]
    markup = hours_inline()
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["start_time"] = start_time
    await bot.edit_message_text("Nechchi soat", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "hour" in call.data.split('|'))
async def hour_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    hour = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["hour"] = hour
        region_filter = data["region_name"]
        district_filter = data["district_name"]
        start_time_str = data["start_time"]
        start_time_filter = datetime.strptime(start_time_str, "%H:%M")
        hour_filter = data["hour"]
    await bot.answer_callback_query(call.id, "Stadionlar")
    # await bot.edit_message_text("Nechchi soat", chat_id, call.message.message_id, reply_markup=markup)
    async with Session() as session:
        order_alias = aliased(Order)
        query = (
            select(Stadium)
            .join(order_alias, Stadium.id == order_alias.stadium_id)
            .filter(func.lower(Stadium.region).ilike(func.lower(region_filter)))
            .filter(func.lower(Stadium.district).ilike(func.lower(district_filter)))
            .filter(order_alias.start_time == start_time_filter)
            .filter(order_alias.hour == hour_filter)
        )

        result = await session.execute(query)
        stadiums = result.scalars().all()
        await bot.send_message(chat_id, "Stadionlar", reply_markup=main_menu_markup())
        await bot.send_message(chat_id, "Tanlang", reply_markup=stadiums_inline(stadiums))
