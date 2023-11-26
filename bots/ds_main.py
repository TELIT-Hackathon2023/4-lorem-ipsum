import os

import discord
from dotenv import load_dotenv
from asyncio import sleep
import detectlanguage

import requests

URL = "http://147.232.156.2:5000/query_request"

BOT_MENTION = "<@1177991649117347850>"


from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()

client = discord.Client(intents=intents, allowed_mentions=discord.AllowedMentions.all())


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


async def get_answer_to_message(message_content_str, thread_id):
    # return "".join(reversed(message_content_str))
    print(message_content_str)
    myobj = {'query': """{}""".format(message_content_str),
         "thread_id": thread_id}

    r = requests.post(URL, json=myobj)
    return r.json()['content']


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        msg_placeholder = await message.reply('Looking for an answer...')

        answer = await get_answer_to_message(message.content.replace(BOT_MENTION, ''), message.author.id)

        await msg_placeholder.edit(content=answer)


client.run(TOKEN)
