from telebot.types import Message
from bot.loader import bot, user_sts, stadium_sts
from bot.owners.markups import main_menu_markup
from bot.owners.markups import your_stadiums_markup


@bot.message_handler(regexp="🔙Bosh sahifa", state="*", is_admin=False, is_owner=True)
async def back_to_main(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    await bot.send_message(chat_id, "Bosh sahifa:", reply_markup=main_menu_markup())
    await bot.set_state(user_id, user_sts.main, chat_id)


@bot.message_handler(regexp="🔙Orqaga", state="*", is_admin=False, is_owner=True)
async def back(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    state = await bot.get_state(user_id, chat_id)

    if state in ["StadiumState:init", "ManageStadiums:edit", "ManageStadiums:choose_stadium"]:
        await bot.send_message(chat_id, "Stadionlar", reply_markup=your_stadiums_markup())
        await bot.set_state(user_id, stadium_sts.init, chat_id)

    else:
        await bot.send_message(chat_id, "Bosh sahifa", reply_markup=main_menu_markup())
        await bot.set_state(user_id, user_sts.main, chat_id)
