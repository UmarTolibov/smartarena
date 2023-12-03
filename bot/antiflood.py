import logging
from telebot.async_telebot import logger
from telebot.asyncio_handler_backends import BaseMiddleware, CancelUpdate, ContinueHandling
from telebot.async_telebot import ExceptionHandler
from telebot.types import Message

logger.setLevel(logging.ERROR)


class HandleException(ExceptionHandler):
    async def handle(self, exception):
        return logging.log(logging.ERROR, exception)


class SimpleMiddleware(BaseMiddleware):
    def __init__(self, limit, bot):
        super().__init__()
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message']
        self.bot = bot

    async def pre_process(self, message: Message, data):
        chat_id = message.chat.id
        user_id = message.from_user.id
        message_id = message.message_id
        if message.content_type == "photo":
            return ContinueHandling()
        if not (message.from_user.id in self.last_time):
            self.last_time[message.from_user.id] = message.date
            return
        if message.date - self.last_time[message.from_user.id] < self.limit:
            await self.bot.delete_message(chat_id, message_id)
            return CancelUpdate()
        self.last_time[message.from_user.id] = message.date

    async def post_process(self, message, data, exception):
        pass
