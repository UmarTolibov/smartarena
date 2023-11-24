from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot import asyncio_filters
from telebot.types import Update, BotCommand

from utils import TOKEN
from bot.common.states import *

bot = AsyncTeleBot(TOKEN, state_storage=StateMemoryStorage())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.ChatFilter())
sts = CustomState()
reg_state = RegistrationState()


async def bot_meta():
    await bot.delete_my_commands()
    await bot.set_my_commands(commands=[BotCommand("start", "to start the bot"),
                                        BotCommand("add_stadium", "to get specific order"),
                                        BotCommand("get_stadium", "to get specific order"),
                                        BotCommand("all_stadiums", "to get all stadiums"),
                                        BotCommand("add_order", "to add stadium"),
                                        BotCommand("get_order", "to get specific order"),
                                        BotCommand("all_orders", "to get all orders"),
                                        BotCommand("cancel", "to cancel any operation")
                                        ])


async def response_to_update(update: Update):
    message = update.message
    callback = update.callback_query
