import telebot.types
from sqlalchemy import select
from telebot.async_telebot import AsyncTeleBot, logger
from telebot.asyncio_storage import StateMemoryStorage
from telebot import asyncio_filters
from telebot.types import BotCommand

from database import Session, User, UserSessions
from .states import Auth, UserState, StadiumState, ManageStadiums, MyBookings, Settings, Help, SuperUserState, \
    OwnerState
from .antiflood import SimpleMiddleware, HandleException
from utils import TOKEN

bot = AsyncTeleBot(TOKEN, state_storage=StateMemoryStorage(), colorful_logs=True, exception_handler=HandleException())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.ChatFilter())
bot.setup_middleware(SimpleMiddleware(1, bot))
auth_sts = Auth()
user_sts = UserState()
stadium_sts = StadiumState()
manage_sts = ManageStadiums()
booking_sts = MyBookings()
settings_sts = Settings()
help_sts = Help()
admin_sts = SuperUserState()
owner_sts = OwnerState()


async def bot_meta():
    await bot.delete_my_commands()
    await bot.set_my_commands(commands=[BotCommand("start", "Botni boshlash"),
                                        BotCommand("cancel", "Bekor qilish"),
                                        BotCommand("logout", "Tizimdan chiqish")
                                        ])


class IsAdmin(asyncio_filters.SimpleCustomFilter):
    key = 'is_admin'

    async def check(self, message):
        user_id = message.from_user.id
        chat_id = message.chat.id if type(message) is not telebot.types.CallbackQuery else message.message.chat.id
        try:
            # await bot.set_state(user_id, NeutralState().init, chat_id)
            async with bot.retrieve_data(user_id, chat_id) as data:
                if data and "is_admin" in data:
                    return data["is_admin"]

        except KeyError as e:
            logger.log(2, "No value id_admin" + e.__str__(), e.args)
        try:
            async with Session() as db:
                admin_q = select(User.is_staff).join(UserSessions, User.id == UserSessions.user_id).where(
                    UserSessions.telegram_id == int(user_id))
                admin = (await db.execute(admin_q)).scalar()
                if admin is not None:
                    if data is not None:
                        data["is_admin"] = admin
                    return admin
        except IndexError as e:
            print("loader/IsAdmin", 59, e)
        except Exception as e:
            print("loader/IsAdmin", 61, e)
        return False


class IsOwner(asyncio_filters.SimpleCustomFilter):
    key = 'is_owner'

    async def check(self, message):
        user_id = message.from_user.id
        chat_id = message.chat.id if type(message) is not telebot.types.CallbackQuery else message.message.chat.id
        try:
            async with bot.retrieve_data(user_id, chat_id) as data:
                if data and "is_owner" in data:
                    return data["is_owner"]

        except KeyError as e:
            logger.log(2, "No value is_owner" + e.__str__(), e.args)
        try:
            async with Session() as db:
                owner_q = select(User.is_owner).join(UserSessions, User.id == UserSessions.user_id).where(
                    UserSessions.telegram_id == int(user_id))
                owner = (await db.execute(owner_q)).scalar()
                if owner is not None:
                    if data is not None:
                        data["is_owner"] = owner
                    return owner
        except IndexError as e:
            print("loader/IsOwner", 88, e)
        except Exception as e:
            print("loader/IsOwner", 90, e)
        return False


bot.add_custom_filter(IsAdmin())
bot.add_custom_filter(IsOwner())
# async def response_to_update(update: Update):
#     message = update.message
#     callback = update.callback_query

#    BotCommand("add_stadium", "to get specific order"),
#    BotCommand("get_stadium", "to get specific order"),
#    BotCommand("all_stadiums", "to get all stadiums"),
#    BotCommand("add_order", "to add stadium"),
#    BotCommand("get_order", "to get specific order"),
#    BotCommand("all_orders", "to get all orders"),
#
