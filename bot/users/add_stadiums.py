from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery
from bot.loader import bot, stadium_sts, user_sts
from database import Stadium, Session
from .markups.buttons import *
from .markups.inline_buttons import *


#  regexp="🏟️Stadionlarim"
@bot.message_handler(regexp="🏟️Stadionlarim")
async def my_stadium_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Stadionlar", reply_markup=your_stadiums_markup())
    await bot.set_state(user_id, stadium_sts.init, chat_id)


# regexp="🌐Stadion qo'shish"
@bot.message_handler(regexp="🌐Stadion qo'shish", state=stadium_sts.init)
async def add_stadium_handler(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, """<b>Stadion yaratish uchun quydagi malumotlar kerak boladi</b>
<i>-Stadion Nomi</i>
<i>-Kantakt malumotlari</i>
<i>-Stadion Rasmlar</i>
<i>-Narxi (soatiga)</i>
<i>-Ochilish vaqti</i>
<i>-Yopilish vaqti</i>
<i>-Viloyat</i>
<i>-Tuman</i>
<i>-Lakatsiya</i>""", reply_markup=back(), parse_mode="html")
    await bot.send_message(chat_id, "Davom ettirasizmi?", reply_markup=yes_no_inline())


# func=lambda call: "proceed" in call.data.split("|"),is_admin=False
@bot.callback_query_handler(func=lambda call: "proceed" in call.data.split("|"), is_admin=False)
async def proceed_yes_no(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    answer = bool(int(call.data.split("|")[1]))
    if answer is True:
        await bot.answer_callback_query(call.id, "Malumotlarni kirishda hushyor bo'lishingizni so'rab qolamiz",
                                        show_alert=True)
        await bot.send_message(chat_id, "Stadion nomini kiriting")
        await bot.set_state(user_id, stadium_sts.name, chat_id)
    else:
        await bot.answer_callback_query(call.id, "Bekor qilindi", )
        await bot.send_message(chat_id, "Bosh sahifa", reply_markup=main_menu_markup())


# content_types=["text"],state=stadium_sts.name
@bot.message_handler(content_types=["text"], state=stadium_sts.name)
async def stadium_name_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium_name"] = message.text
    await bot.send_message(chat_id, "Stadion kontakt/malumotlarinini jo'nating")
    await bot.set_state(user_id, stadium_sts.description, chat_id)


# content_types=["text"],state=stadium_sts.description
@bot.message_handler(content_types=["text"], state=stadium_sts.description)
async def stadium_desc_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium_description"] = message.text
        data["photo"] = 0
        data["stadium_photo"] = []
    await bot.send_message(chat_id, "Stadion uchun rasmlarni jo'nating va tugmani bosing", reply_markup=done())
    await bot.set_state(user_id, stadium_sts.image, chat_id)


# content_types=["photo", "text"],state=stadium_sts.image
@bot.message_handler(content_types=["photo", "text"], state=stadium_sts.image)
async def stadium_image_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.content_type == "photo":
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["stadium_photo"].append(message.json["photo"][-1]["file_id"])
    if message.content_type == "text" and message.text == "Jo'natib bo'ldim👌":
        await bot.send_message(chat_id, "Stadion narxini yuboring (so'm/soat)")
        await bot.set_state(user_id, stadium_sts.price, chat_id)


# content_types=["text"],state=stadium_sts.price
@bot.message_handler(content_types=["text"], state=stadium_sts.price)
async def stadium_price_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium_price"] = message.text
    await bot.send_message(chat_id, "Stadioning ochilish vaqti🕒", reply_markup=start_time_inline(1))
    await bot.set_state(user_id, stadium_sts.open_time, chat_id)


# func=lambda call: "s_time" in call.data.split("|"),state=stadium_sts.open_time
@bot.callback_query_handler(func=lambda call: "s_time" in call.data.split("|"), state=stadium_sts.open_time)
async def stadium_open_time_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium_open_time"] = call.data.split("|")[1]
        await bot.answer_callback_query(call.id, f"Ochilish vaqti: {call.data.split('|')[1]}")
        await bot.edit_message_text("Stadionning Yopilish Vaqti🕟:", chat_id, call.message.message_id,
                                    reply_markup=start_time_inline(2))
        await bot.set_state(user_id, stadium_sts.close_time, chat_id)


# func=lambda call: "c_time" in call.data.split("|"),state=stadium_sts.close_time
@bot.callback_query_handler(func=lambda call: "c_time" in call.data.split("|"), state=stadium_sts.close_time)
async def stadium_close_time_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium_close_time"] = call.data.split("|")[1]
        await bot.answer_callback_query(call.id, f"Yopilish vaqti: {call.data.split('|')[1]}")
        await bot.edit_message_text("Stadion joylashgan Viloyat", chat_id, call.message.message_id,
                                    reply_markup=regions_inline(1))
        await bot.set_state(user_id, stadium_sts.region, chat_id)


# func=lambda call: "add_region" in call.data.split('|'),state=stadium_sts.region
@bot.callback_query_handler(func=lambda call: "add_region" in call.data.split('|'), state=stadium_sts.region)
async def stadium_region_handler(call: CallbackQuery):
    from utils.config import regions_file_path
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    region_id = int(call.data.split("|")[1])
    markup = district_inline(region_id, 1)
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium_region"] = region_id
        with open(regions_file_path, "r", encoding="utf-8") as file:
            region = json.load(file)["regions"][region_id - 1]
        data["region_name"] = region['name']
    await bot.edit_message_text("Tumanni tanlang", chat_id, call.message.message_id, reply_markup=markup)
    await bot.set_state(user_id, stadium_sts.district, chat_id)


# func=lambda call: "add_district" in call.data.split('|'),state=stadium_sts.district
@bot.callback_query_handler(func=lambda call: "add_district" in call.data.split('|'), state=stadium_sts.district)
async def district_choose(call: CallbackQuery):
    from utils.config import regions_file_path

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    district_id = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["stadium_district"] = district_id
        with open(regions_file_path, "r", encoding="utf-8") as file:
            district = json.load(file)["districts"][district_id - 15]
            data["district_name"] = district['name']
    await bot.send_message(chat_id, "Stadion joylashux nuqtasini(lokatsya) jo'nating", reply_markup=request_location())
    await bot.set_state(user_id, stadium_sts.location, chat_id)


# content_types=["location"],state=stadium_sts.location
@bot.message_handler(content_types=["location"], state=stadium_sts.location)
async def stadium_location_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["location_data"] = {"longitude": message.location.longitude, "latitude": message.location.latitude}
        name = data["stadium_name"]
        desc = data["stadium_description"]
        price = int(data["stadium_price"])
        open_time = data["stadium_open_time"]
        close_time = data["stadium_close_time"]
        region = data["region_name"]
        district = data["district_name"]

    stadium_data = f"""<b>Nomi:</b> <code>{name}</code>
<b>Stadion haqida:</b><code>{desc}</code>
<b>Narxi:</b> <code>{price} </code>so'm/soat
<b>Ochilish vaqti:</b><code> {open_time}</code>
<b>Yopilish vaqti:</b> <code>{close_time}</code>
<b>Viloyat/shahar:</b> <code>{region}</code>
<b>Tuman:</b> <code>{district}</code>"""
    await bot.send_message(chat_id, "Stadion Malumotlarini Tasdiqlang:", reply_markup=ReplyKeyboardRemove())
    await bot.send_message(chat_id, f"{stadium_data}",
                           reply_markup=confirmation(), parse_mode="html")
    await bot.set_state(user_id, stadium_sts.confirm, chat_id)


# func=lambda call: call.data in ("confirm", "reject"), state=stadium_sts.confirm,is_admin=False
@bot.callback_query_handler(func=lambda call: call.data in ("confirm", "reject"), state=stadium_sts.confirm, is_admin=False)
async def stadium_confirmation_handler(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    if callback.data == "confirm":
        async with bot.retrieve_data(user_id, chat_id) as data:
            new_stadium = Stadium(name=data["stadium_name"], description=data["stadium_description"],
                                  price=int(data["stadium_price"]), opening_time=data["stadium_open_time"],
                                  closing_time=data["stadium_close_time"], region=data["region_name"],
                                  district=data["district_name"], location=data["location_data"],
                                  user_id=data["user_id"])
            new_stadium.set_image_urls(data["stadium_photo"])

        try:
            async with Session() as db:
                db.add(new_stadium)
                await db.commit()
            await bot.send_message(chat_id, "Stadion qo'shildi.", reply_markup=main_menu_markup())
            await bot.set_state(user_id, user_sts.main, chat_id)
        except Exception as e:
            print(e)
            await bot.send_message(chat_id, "Hatolik yuz berdi, qayta urinib ko'ring:(",
                                   reply_markup=your_stadiums_markup())
            await bot.set_state(chat_id, stadium_sts.init, user_id)
    if callback.data == "reject":
        await bot.send_message(chat_id, "Stadion nomini kiriting", reply_markup=back())
        await bot.set_state(user_id, stadium_sts.name, chat_id)
