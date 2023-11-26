import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from asyncio import sleep
import requests


URL = "http://147.232.156.2:5000/query_request"

load_dotenv()
TG_API = os.getenv("TELEGRAM_API_KEY")

bot = Bot(token=TG_API)
dp = Dispatcher(bot)


async def on_startup(_):
    print("Bot is alive")


async def on_shutdown(_):
    print("Bot is offline")



async def get_answer_to_message(message_content_str, thread_id):
    # return "".join(reversed(message_content_str))
    print(message_content_str)
    myobj = {'query': """{}""".format(message_content_str),
         "thread_id": thread_id}

    r = requests.post(URL, json=myobj)
    return r.json()['content']


async def on_message(message: types.Message):
    msg_placeholder = await message.reply('Looking for an answer...')

    answer = await get_answer_to_message(message.text, message.from_user.id)

    await msg_placeholder.edit_text(text=answer)


def register_client_handlers(_dp: Dispatcher):
    _dp.register_message_handler(on_message)


register_client_handlers(dp)
executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
