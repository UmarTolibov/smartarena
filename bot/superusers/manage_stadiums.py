from sqlalchemy import select, delete, update
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from bot.loader import bot, stadium_sts, manage_sts
from database import Stadium, Session
from bot.owners.markups.buttons import *
from bot.owners.markups.inline_buttons import *


@bot.message_handler(regexp="🛠️Stadionlarimni boshqarish", state=stadium_sts.init, is_admin=True)
async def manage_stadium_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        stadiums_query = select(Stadium.name, Stadium.id).where(Stadium.user_id == data["user_id"])
    async with Session.begin() as db:
        stadiums = (await db.execute(stadiums_query)).fetchall()
        markup = stadiums_choose(stadiums)
    await bot.send_message(chat_id,"Stadionni", reply_markup=back())
    await bot.send_message(chat_id, "tanlang", reply_markup=markup)
    await bot.set_state(user_id, manage_sts.choose_stadium, chat_id)


@bot.callback_query_handler(func=lambda call: "stadium" in call.data.split("|"), state=manage_sts.choose_stadium,
                            is_admin=True)
async def stadium_to_manage(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = int(call.data.split("|")[1])
    async with Session() as db:
        s_query = select(Stadium).where(Stadium.id == data)
        stadium = (await db.execute(s_query)).scalar()
        images = [InputMediaPhoto(i) for i in json.loads(stadium.image_urls)]
        markup = manage_stadium(data)
        message = f"""
<b>Nomi:</b> {stadium.name}
<b>Ma'lumot:</b> {stadium.description}
<b>Narxi:</b> {stadium.price} so'm/soat
<b>Ochilish vaqti:</b> {stadium.opening_time}
<b>Yopilish vaqti:</b> {stadium.closing_time}
<b>Viloyat:</b> {stadium.region}
<b>Tuman:</b> <i>{stadium.district}</i>"""
        sent_loc = await bot.send_location(chat_id, **stadium.location, reply_markup=back())
        sent_me = await bot.send_media_group(chat_id, images)
        sent_message = await bot.send_message(chat_id, message, parse_mode="html", reply_markup=markup)
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["sent_loc"] = sent_loc.message_id
            data["sent_media"] = [i.message_id for i in sent_me]
            data["sent_message"] = sent_message.message_id
        await bot.set_state(user_id, manage_sts.edit, chat_id)
        await bot.answer_callback_query(call.id, "yangilash")


@bot.callback_query_handler(func=lambda call: True, state=manage_sts.edit, is_admin=True)
async def delete_stadium(call: CallbackQuery):
    if call.data.split("|")[1] == "delete":
        chat_id = call.message.chat.id
        stadium_id = int(call.data.split("|")[2])
        async with Session.begin() as db:
            query = delete(Stadium).where(Stadium.id == stadium_id)
            await db.execute(query)
            await db.commit()
            await bot.answer_callback_query(call.id, "Stadion o'chirildi")
            await bot.send_message(chat_id, "Bosh menu:", reply_markup=your_stadiums_markup())
            await bot.delete_message(chat_id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: True, state=manage_sts.edit, is_admin=True)
async def refresh_stadium(call: CallbackQuery):
    if call.data.split("|")[1] == "refresh":
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        stadium_id = int(call.data.split("|")[2])
        await bot.answer_callback_query(call.id, "Yangilanyapti")
        async with Session() as db:
            s_query = select(Stadium).where(Stadium.id == stadium_id)
            stadium = (await db.execute(s_query)).scalar()
            images = [InputMediaPhoto(i) for i in json.loads(stadium.image_urls)]
            markup = manage_stadium(stadium_id)
            message = f"""
    <b>Nomi:</b> {stadium.name}
    <b>Ma'lumot:</b> {stadium.description}
    <b>Narxi:</b> {stadium.price} so'm/soat
    <b>Ochilish vaqti:</b> {stadium.opening_time}
    <b>Yopilish vaqti:</b> {stadium.closing_time}
    <b>Viloyat:</b> {stadium.region}
    <b>Tuman:</b> <i>{stadium.district}</i>"""
            async with bot.retrieve_data(user_id, chat_id) as data:
                await bot.delete_message(chat_id, data["sent_loc"])
                await bot.delete_message(chat_id, data["sent_message"])
                for i in data["sent_media"]:
                    await bot.delete_message(chat_id, i)

                sent_loc = await bot.send_location(chat_id, **stadium.location, reply_markup=back())
                sent_me = await bot.send_media_group(chat_id, images)
                sent_message = await bot.send_message(chat_id, message, parse_mode="html",
                                                      reply_markup=markup)
                data["sent_loc"] = sent_loc.message_id
                data["sent_media"] = [i.message_id for i in sent_me]
                data["sent_message"] = sent_message.message_id


@bot.callback_query_handler(state=manage_sts.edit,
                            func=lambda call: call.data.split("|")[1] in ["name", "desc", "image_urls", "price",
                                                                          "otime", "ctime", "reg",
                                                                          "disc", "location"], is_admin=True)
async def edit_stadium_data(call: CallbackQuery):
    print(call.data + "_+" * 23)

    from utils.config import regions_file_path

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    target = call.data.split("|")[1]
    stadium_id = int(call.data.split("|")[2])
    async with Session.begin() as db:
        stadium_region = (await db.execute(select(Stadium.region).where(Stadium.id == stadium_id))).scalar()
    with open(regions_file_path, "r", encoding="utf-8") as file:
        region_id = list(filter(lambda x: x["name"] == stadium_region, json.load(file)["regions"]))[0]["id"]
        if target == "location":
            sent = await bot.send_message(chat_id, "Yangi Lokatsiyani jo'nating",
                                          reply_markup=request_location())
            await bot.set_state(user_id, manage_sts.location, chat_id)
        elif target == "image":
            sent = await bot.send_message(chat_id, "Yangi Rasmlarni jo'nating va tugmani bosing",
                                          reply_markup=done())
            await bot.set_state(user_id, manage_sts.image, chat_id)
        elif target == "reg":
            sent = await bot.send_message(chat_id, "Yangi Viloyatni tanlang", reply_markup=regions_inline(1))
            await bot.set_state(user_id, manage_sts.region, chat_id)
        elif target == "disc":
            sent = await bot.send_message(chat_id, "Yangi Tumanni tanlang",
                                          reply_markup=district_inline(region_id, for_add=1))
            await bot.set_state(user_id, manage_sts.district, chat_id)
        elif target == "otime":
            sent = await bot.send_message(chat_id, "Ochilish vaqtini o'zgartirish",
                                          reply_markup=start_time_inline(1))
            await bot.set_state(user_id, manage_sts.open_time, chat_id)
        elif target == "ctime":
            sent = await bot.send_message(chat_id, "Yopilish vaqtini o'zgartirish",
                                          reply_markup=start_time_inline(2))
            await bot.set_state(user_id, manage_sts.close_time, chat_id)
        elif target == "name":
            sent = await bot.send_message(chat_id, "Stadion uchun yangi nomni jo'nating")
            await bot.set_state(user_id, manage_sts.name, chat_id)
        elif target == "price":
            sent = await bot.send_message(chat_id, "Stadion uchun yangi narxni jo'nating")
            await bot.set_state(user_id, manage_sts.price, chat_id)
        else:
            sent = await bot.send_message(chat_id, "Stadion uchun yangi ma'lumotni jo'nating")
            await bot.set_state(user_id, manage_sts.description, chat_id)
        await bot.answer_callback_query(call.id, "yangilash")
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["edit_stadium_id"] = stadium_id
            data["sent_message_id"] = sent.message_id


@bot.message_handler(content_types=["text"], state=manage_sts.name, is_admin=True)
async def stadium_edit_name_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["sent_message_id"])
        stadium_id = data["edit_stadium_id"]
    async with Session.begin() as db:
        q = update(Stadium).where(Stadium.id == stadium_id).values(name=text)
        await db.execute(q)
        await db.commit()
    sent = await bot.send_message(chat_id, "Stadion nomi yangilandi!", reply_markup=your_stadiums_markup())
    await bot.set_state(user_id, manage_sts.edit, chat_id)
    await bot.delete_message(chat_id, message.message_id)
    await bot.delete_message(chat_id, sent.message_id)


@bot.message_handler(content_types=["text"], state=manage_sts.description, is_admin=True)
async def stadium_desc_edit_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["sent_message_id"])
        stadium_id = data["edit_stadium_id"]
    async with Session.begin() as db:
        q = update(Stadium).where(Stadium.id == stadium_id).values(description=text)
        await db.execute(q)
        await db.commit()
    sent = await bot.send_message(chat_id, "Stadion malumoti yangilandi!", reply_markup=your_stadiums_markup())
    await bot.set_state(user_id, manage_sts.edit, chat_id)
    await bot.delete_message(chat_id, message.message_id)
    await bot.delete_message(chat_id, sent.message_id)


@bot.message_handler(content_types=["location"], state=manage_sts.location, is_admin=True)
async def stadium_edit_location_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    location = {"longitude": message.location.longitude, "latitude": message.location.latitude}
    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["sent_message_id"])
        stadium_id = data["edit_stadium_id"]
    async with Session.begin() as db:
        q = update(Stadium).where(Stadium.id == stadium_id).values(location=location)
        await db.execute(q)
        await db.commit()
    sent = await bot.send_message(chat_id, "Stadion lokatsiyasi yangilandi!", reply_markup=your_stadiums_markup())
    await bot.set_state(user_id, manage_sts.edit, chat_id)
    await bot.delete_message(chat_id, message.message_id)
    await bot.delete_message(chat_id, sent.message_id)


@bot.message_handler(content_types=["photo", "text"], state=manage_sts.image, is_admin=True)
async def stadium_edit_image_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    images = []
    if message.content_type == "photo":
        async with bot.retrieve_data(user_id, chat_id) as data:
            await bot.delete_message(chat_id, data["sent_message_id"])
            stadium_id = data["edit_stadium_id"]
            images.append(message.json["photo"][-1]["file_id"])
    if message.content_type == "text" and message.text == "Jo'natib bo'ldim👌":
        async with Session.begin() as db:
            q = update(Stadium).where(Stadium.id == stadium_id).values(image_urls=images)
            await db.execute(q)
            await db.commit()
        sent = await bot.send_message(chat_id, "Stadion rasmlari yangilandi", reply_markup=your_stadiums_markup())
        await bot.set_state(user_id, manage_sts.edit, chat_id)
        await bot.delete_message(chat_id, message.message_id)
        await bot.delete_message(chat_id, sent.message_id)


@bot.message_handler(content_types=["text"], state=manage_sts.price, is_admin=True)
async def stadium_edit_price_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    price = int(message.text)
    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["sent_message_id"])
        stadium_id = data["edit_stadium_id"]
    async with Session.begin() as db:
        q = update(Stadium).where(Stadium.id == stadium_id).values(price=price)
        await db.execute(q)
        await db.commit()
        sent = await bot.send_message(chat_id, "Stadion narxi yangilandi", reply_markup=your_stadiums_markup())
        await bot.set_state(user_id, manage_sts.edit, chat_id)
        await bot.delete_message(chat_id, message.message_id)
        await bot.delete_message(chat_id, sent.message_id)


@bot.callback_query_handler(func=lambda call: "s_time" in call.data.split("|"), state=manage_sts.open_time,
                            is_admin=True)
async def stadium_edit_open_time_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    opening_time = call.data.split("|")[1]
    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["sent_message_id"])
        stadium_id = data["edit_stadium_id"]
    async with Session.begin() as db:
        q = update(Stadium).where(Stadium.id == stadium_id).values(opening_time=opening_time)
        await db.execute(q)
        await db.commit()
        await bot.answer_callback_query(call.id, "Stadion ochilish vaqti yangilandi")
        sent = await bot.send_message(chat_id, "Yangilandi", reply_markup=your_stadiums_markup())
        await bot.set_state(user_id, manage_sts.edit, chat_id)
        await bot.delete_message(chat_id, sent.message_id)


@bot.callback_query_handler(func=lambda call: "c_time" in call.data.split("|"), state=manage_sts.close_time,
                            is_admin=True)
async def stadium_edit_close_time_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    closing_time = call.data.split("|")[1]

    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["sent_message_id"])
        stadium_id = data["edit_stadium_id"]
    async with Session.begin() as db:
        q = update(Stadium).where(Stadium.id == stadium_id).values(closing_tim=closing_time)
        await db.execute(q)
        await db.commit()
        await bot.answer_callback_query(call.id, "Stadion yopilish vaqti yangilandi")
        sent = await bot.send_message(chat_id, "Yangilandi", reply_markup=your_stadiums_markup())
        await bot.set_state(user_id, manage_sts.edit, chat_id)
        await bot.delete_message(chat_id, sent.message_id)


@bot.callback_query_handler(func=lambda call: "add_region" in call.data.split('|'), state=manage_sts.region,
                            is_admin=True)
async def stadium_edit_region_handler(call: CallbackQuery):
    from utils.config import regions_file_path
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    print(call.data)
    region_id = int(call.data.split("|")[1])

    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["sent_message_id"])
        stadium_id = data["edit_stadium_id"]
        with open(regions_file_path, "r", encoding="utf-8") as file:
            region = json.load(file)["regions"][region_id - 1]["name"]

    async with Session.begin() as db:
        q = update(Stadium).where(Stadium.id == stadium_id).values(region=region)
        await db.execute(q)
        await db.commit()
        await bot.answer_callback_query(call.id, "Stadion Viloyati yangilandi")
        sent = await bot.send_message(chat_id, "Yangilandi", reply_markup=your_stadiums_markup())
        await bot.set_state(user_id, manage_sts.edit, chat_id)
        await bot.delete_message(chat_id, sent.message_id)


@bot.callback_query_handler(func=lambda call: "add_district" in call.data.split('|'), state=manage_sts.district,
                            is_admin=True)
async def edit_district_choose(call: CallbackQuery):
    from utils.config import regions_file_path
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    print(call.data)
    district_id = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as data:
        await bot.delete_message(chat_id, data["sent_message_id"])
        stadium_id = data["edit_stadium_id"]
        with open(regions_file_path, "r", encoding="utf-8") as file:
            district = json.load(file)["districts"][district_id - 15]["name"]
    async with Session.begin() as db:
        q = update(Stadium).where(Stadium.id == stadium_id).values(district=district)
        await db.execute(q)
        await db.commit()
        await bot.answer_callback_query(call.id, "Stadion yopilish vaqti yangilandi")
        sent = await bot.send_message(chat_id, "Yangilandi", reply_markup=your_stadiums_markup())
        await bot.set_state(user_id, manage_sts.edit, chat_id)
        await bot.delete_message(chat_id, sent.message_id)
