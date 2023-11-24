from database.connection import Session
from database import User, Stadium, Order
from sqlalchemy.sql import select, delete, or_, and_

from bot.loader import bot, sts
from telebot.types import CallbackQuery


# =======================================================================================
# To delete stadium

@bot.callback_query_handler(func=lambda c: c.data.split("|")[0] == "s_delete", state='*')
async def delete_stadium(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    stadium_id = int(call.data.split('|')[1])
    async with Session.begin() as db:
        stadium_get_query = select(Stadium.user_id).where(Stadium.id == stadium_id)
        stadium_del_query = delete(Stadium).where(Stadium.id == stadium_id)
        stadium = (await db.execute(stadium_get_query)).scalar()
        user_query = select(User).where(
            or_(and_(User.telegram_id == user_id, stadium == User.id), User.is_staff))
        user = (await db.execute(user_query)).scalar()
        if user:
            await db.execute(stadium_del_query)
            await db.commit()
            await bot.delete_message(chat_id, call.message.message_id)
            await bot.answer_callback_query(call.id, "Deleted✅", show_alert=True)
            await bot.delete_state(user_id, chat_id)
        else:
            await bot.send_message(chat_id, "This action is not permitted for you")


# =======================================================================================
# To edit stadium


@bot.callback_query_handler(func=lambda c: c.data.split("|")[0] == "s_edit", state='*')
async def edit_stadium(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    stadium_id = int(call.data.split('|')[1])
    await bot.set_state(user_id, sts.edit, chat_id)
    async with bot.retrieve_data(user_id, chat_id) as data:
        data['id'] = stadium_id
        data["message"] = call.message.message_id
        async with Session.begin() as db:
            stadium_get_query = select(Stadium).where(Stadium.id == stadium_id)
            stadium = (await db.execute(stadium_get_query)).scalar()

            user_query = select(User).where(
                or_(and_(User.telegram_id == user_id, stadium.user_id == User.id), User.is_staff))

            user = (await db.execute(user_query)).scalar()
            if user:
                request_msg = await bot.send_message(chat_id,
                                                     """Please send the stadium info in json format! Example:<code>{
                                                     "name":"new name", "image_url":"new image url"}</code>""",
                                                     parse_mode="html")
                await bot.set_state(user_id, sts.edit, chat_id)
                data['message2'] = request_msg.message_id
            else:
                await bot.send_message(chat_id, "You are not permitted to do this action")
                await bot.delete_message(chat_id, call.message.message_id)


# =======================================================================================
# To delete order

@bot.callback_query_handler(func=lambda c: c.data.split("|")[0] == "o_delete", state='*')
async def delete_stadium(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    order_id = int(call.data.split('|')[1])
    async with Session.begin() as db:
        order_get_query = select(Order.user_id).where(Order.id == order_id)
        order_del_query = delete(Order).where(Order.id == order_id)
        order = (await db.execute(order_get_query)).scalar()
        user_query = select(User).where(
            or_(and_(User.telegram_id == user_id, order == User.id), User.is_staff))
        user = (await db.execute(user_query)).scalar()
        if user:
            await db.execute(order_del_query)
            await db.commit()
            await bot.delete_message(chat_id, call.message.message_id)
            await bot.answer_callback_query(call.id, "Deleted✅", show_alert=True)
            await bot.delete_state(user_id, chat_id)
        else:
            await bot.send_message(chat_id, "This action is not permitted for you")


# =======================================================================================
# To edit order


@bot.callback_query_handler(func=lambda c: c.data.split("|")[0] == "o_edit", state='*')
async def edit_order(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    order_id = int(call.data.split('|')[1])
    await bot.set_state(user_id, sts.edit, chat_id)
    async with bot.retrieve_data(user_id, chat_id) as data:
        data['id'] = order_id
        data["message"] = call.message.message_id
        async with Session.begin() as db:
            order_get_query = select(Order).where(Order.id == order_id)
            order = (await db.execute(order_get_query)).scalar()

            user_query = select(User).where(
                or_(and_(User.telegram_id == user_id, order.user_id == User.id), User.is_staff))

            user = (await db.execute(user_query)).scalar()
            if user:
                request_msg = await bot.send_message(chat_id,
                                                     """Please send the order info in json format! Example:<code>{
                                                     "status":"APPROVED", "hour": 4}</code>""",
                                                     parse_mode="html")
                await bot.set_state(user_id, sts.o_edit, chat_id)
                data['message2'] = request_msg.message_id
            else:
                await bot.send_message(chat_id, "You are not permitted to do this action")
                await bot.delete_message(chat_id, call.message.message_id)
