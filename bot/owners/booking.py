from sqlalchemy import select, func, exists, and_
from sqlalchemy.orm import aliased
from telebot.types import CallbackQuery

from bot.loader import bot, user_sts
from database import Stadium, Order, Session
from bot.owners.markups.buttons import *
from bot.owners.markups.inline_buttons import *


@bot.callback_query_handler(func=lambda call: "hour" in call.data.split('|'), is_owner=True, is_admin=False)
async def owner_hour_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    hour = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["hour"] = hour
        region_filter = data["region_name"]
        district_filter = data["district_name"]
        start_time_str = data["start_time"]
        date_str = data["date"]
        date_object = datetime.datetime.strptime(date_str.replace(":", "-"), "%Y-%m-%d")
        start_time_delta = datetime.datetime.strptime(start_time_str, "%H:%M").time()
        combined_datetime = datetime.datetime.combine(date_object, start_time_delta)
        hour_filter = data["hour"]
        markup = main_menu_markup()
    await bot.answer_callback_query(call.id, "Stadionlar")
    async with Session() as session:
        order_alias = aliased(Order)
        query = (
            select(Stadium)
            .filter(func.lower(Stadium.region).ilike(func.lower(region_filter)))
            .filter(func.lower(Stadium.district).ilike(func.lower(district_filter)))
            .filter(~exists().where(
                and_(
                    order_alias.stadium_id == Stadium.id,
                    order_alias.start_time == combined_datetime,
                    order_alias.hour == hour_filter
                )
            ))
        )

        # Execute the query asynchronously to get the result
        result = await session.execute(query)
        stadiums = result.scalars().all()
        if stadiums is None or len(stadiums) == 0:
            await bot.send_message(chat_id, "Berilgan filterlar boyicha stadionlar mavjud emas yoki Band!",
                                   reply_markup=markup)
        else:
            await bot.set_state(user_id, user_sts.preview, chat_id)
            await bot.send_message(chat_id, "Stadionlar", reply_markup=markup)
            await bot.send_message(chat_id, "Tanlang", reply_markup=stadiums_inline(stadiums))


@bot.callback_query_handler(func=lambda call: call.data in ["book_now", "send_location"], is_owner=True,
                            is_admin=False)
async def admin_location_book(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    if data == "book_now":
        # format_string = "%Y-%m-%d %H:%M:%S"
        async with bot.retrieve_data(user_id, chat_id) as data:
            start_time_str = data["start_time"]
            date_str = data["date"]
            date_object = datetime.datetime.strptime(date_str.replace(":", "-"), "%Y-%m-%d")
            start_time_delta = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            combined_datetime = datetime.datetime.combine(date_object, start_time_delta)
            hour = data["hour"]
            new_order = Order(status="Ko'rib chiqilmoqda", start_time=combined_datetime, hour=hour,
                              user_id=data["user_id"],
                              stadium_id=data["stadium_id"])
        try:
            async with Session() as db:
                db.add(new_order)
                await db.commit()
            await bot.answer_callback_query(call.id, f"Bajarildi✅")
            await bot.send_message(chat_id, "Stadion bron qilindi", reply_markup=main_menu_markup())
            await bot.set_state(user_id, user_sts.main, chat_id)

        except Exception as e:
            print(e)
    else:
        await bot.answer_callback_query(call.id, f"Lokatsiya")
        async with bot.retrieve_data(user_id, chat_id) as bdata:
            location = bdata["location"]
        await bot.send_location(chat_id, **location, reply_markup=book_inline(True))
