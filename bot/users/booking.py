from sqlalchemy import select, func, exists, and_
from sqlalchemy.orm import aliased
from telebot.types import Message, CallbackQuery, InputMediaPhoto

from bot.loader import bot, user_sts
from database import Stadium, Order, Session, User, UserSessions
from .markups.buttons import *
from .markups.inline_buttons import *


@bot.message_handler(regexp="📆Bron qilish")
async def book_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with Session() as db:
        user_q = select(UserSessions.user_id).where(UserSessions.telegram_id == user_id)
        user = (await db.execute(user_q)).scalar()
        stadium_q = select(Stadium).join(Order, Stadium.id == Order.stadium_id).where(Order.user_id == user)
        stadium = (await db.execute(stadium_q)).scalars().all()

    if len(stadium) == 0:
        await bot.send_message(chat_id, "Bron qilish", reply_markup=back())
        await bot.send_message(chat_id, "Viloyatni tanlang", reply_markup=regions_inline())
        await bot.set_state(user_id, user_sts.region, chat_id)
    else:
        stadiums = []
        for i in stadium:
            if (i.name, i.id) not in stadiums:
                stadiums.append((i.name, i.id))
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["last_books"] = stadiums
        await bot.send_message(chat_id, "Bron qilish", reply_markup=quickbook_simplebook())


@bot.message_handler(regexp="Bron qilish📆")
async def simple_book_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Bron qilish", reply_markup=back())
    await bot.send_message(chat_id, "Viloyatni tanlang", reply_markup=regions_inline())
    await bot.set_state(user_id, user_sts.region, chat_id)


@bot.message_handler(regexp="Oldingi bronlar📆")
async def quick_book_stadium(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        markup = booked_stadiums_choose(data["last_books"])
    await bot.send_message(chat_id, "Bronlar", reply_markup=back())
    await bot.send_message(chat_id, "Stadionni tanlang!", reply_markup=markup)
    await bot.set_state(user_id, user_sts.preview, chat_id)


@bot.callback_query_handler(func=lambda call: "region" in call.data.split('|'), state=user_sts.region)
async def region_choose(call: CallbackQuery):
    from utils.config import regions_file_path

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    region_id = int(call.data.split("|")[1])
    markup = district_inline(region_id)
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["region"] = region_id
        with open(regions_file_path, "r", encoding="utf-8") as file:
            region = json.load(file)["regions"][region_id - 1]
        data["region_name"] = region['name']
    sent = await bot.send_message(chat_id, f"{region['name']}")
    await bot.delete_message(chat_id, sent.message_id)
    await bot.set_state(user_id, user_sts.district, chat_id)
    await bot.edit_message_text("Tumanni tanlang", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "district" in call.data.split('|'), state=user_sts.district)
async def district_choose(call: CallbackQuery):
    from utils.config import regions_file_path
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    district_id = int(call.data.split("|")[1])
    markup = date_time()
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["district"] = district_id
        with open(regions_file_path, "r", encoding="utf-8") as file:
            district = json.load(file)["districts"][district_id - 15]
            data["district_name"] = district['name']
    await bot.set_state(user_id, user_sts.date, chat_id)
    await bot.edit_message_text("Sanani Tanlang", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "date" in call.data.split("|"), state=user_sts.date)
async def date_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    date = call.data.split("|")[1]
    markup = start_time_inline()
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["date"] = date
    await bot.set_state(user_id, user_sts.start_time, chat_id)
    await bot.edit_message_text("Boshlash vaqti", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "start_time" in call.data.split('|'), state=user_sts.start_time)
async def start_time_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    start_time = call.data.split("|")[1]
    markup = hours_inline()
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["start_time"] = start_time
    await bot.set_state(user_id, user_sts.hour, chat_id)
    await bot.edit_message_text("Nechchi soat", chat_id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: "hour" in call.data.split('|'), is_admin=False, state=user_sts.hour)
async def hour_choose(call: CallbackQuery):
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


@bot.callback_query_handler(func=lambda call: "book" in call.data.split("|"), state=user_sts.preview)
async def stadium_preview(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as bdata:
        bdata["stadium_id"] = data

    async with Session.begin() as db:
        stadium_q = select(Stadium).where(Stadium.id == data)
        stadium = (await db.execute(stadium_q)).scalar()
        message = f"""<b>Nomi:</b> {stadium.name}
<b>Ma'lumot:</b> {stadium.description}
<b>Narxi:</b> {stadium.price} so'm/soat
<b>Ochilish vaqti:</b> {stadium.opening_time}
<b>Yopilish vaqti:</b> {stadium.closing_time}
<b>Viloyat:</b> {stadium.region}
<b>Tuman:</b> <i>{stadium.district}</i>"""
        bdata["location"] = stadium.location
        image_urls = json.loads(stadium.image_urls)
        images = []
        for i in image_urls:
            images.append(InputMediaPhoto(i))
        await bot.set_state(user_id, user_sts.loc_book, chat_id)
        await bot.send_media_group(chat_id, images)
        await bot.send_message(chat_id, message, parse_mode="html", reply_markup=book_inline())
        await bot.answer_callback_query(call.id, f"stadion {stadium.name}")


@bot.callback_query_handler(func=lambda call: call.data in ["book_now", "send_location"], is_admin=False,
                            state=user_sts.loc_book)
async def location_book(call: CallbackQuery):
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
                await db.refresh(new_order)

            async with Session() as db:
                q_s = select(Stadium).where(Stadium.id == new_order.stadium_id)
                q_u = select(User).where(User.id == new_order.user_id)
                stadium = (await (db.execute(q_s))).scalar()
                user = (await (db.execute(q_u))).scalar()
                text = f"""<b>Stadion</b>: <code>{stadium.name}</code>
<b>Boshlanish vaqti</b>: <code>{combined_datetime}</code>
<b>Soat</b>: <code>{hour}</code>

<b>Buyurtmachi</b>: <b>{user.username}</b> 
<b>raqami</b>: <code>{user.number}</code>
<b>email</b>: <code>{user.email}</code>

#{stadium.region.replace(" ", "_")}, #{stadium.district.replace(" ", "_")}, #{stadium.name.replace(" ", "_")}
"""
            await bot.answer_callback_query(call.id, f"Bajarildi✅")
            await bot.send_message(chat_id, "Stadion bron qilindi", reply_markup=main_menu_markup())
            await bot.send_message(-1002049070221, text, parse_mode="html")
            await bot.set_state(user_id, user_sts.main, chat_id)

        except Exception as e:
            print(e)
    else:
        await bot.answer_callback_query(call.id, f"Lokatsiya")
        async with bot.retrieve_data(user_id, chat_id) as bdata:
            location = bdata["location"]
        await bot.set_state(user_id, user_sts.loc_book, chat_id)
        await bot.send_location(chat_id, **location, reply_markup=book_inline(True))
