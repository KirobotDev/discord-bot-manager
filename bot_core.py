import discord
from discord.ext import commands
import os
import multiprocessing
import sys
import io
import logging
import queue
import asyncio

bot = None
process = None

async def bot_main(token, log_queue):
    global bot
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('discord')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(handler)
    
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    @bot.event
    async def on_ready():
        log_queue.put(f"INFO discord.client Connected as {bot.user}")
    
    @bot.event
    async def on_message(message):
        log_queue.put(f"INFO discord.client {message.author}: {message.content}")
        await bot.process_commands(message)
    
    @bot.event
    async def on_command_error(ctx, error):
        log_queue.put(f"ERROR discord.ext.commands.bot {error}")
    
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            try:
                cog_name = file[:-3]
                await bot.load_extension(f"cogs.{cog_name}")
                log_queue.put(f"INFO discord.ext.commands.bot Loaded cog {cog_name}")
            except Exception as e:
                log_queue.put(f"ERROR discord.ext.commands.bot Failed to load cog {file}: {str(e)}")
    
    await bot.start(token)
    
    sys.stdout = original_stdout

def start_bot(token, log_queue):
    global process
    process = multiprocessing.Process(target=lambda: asyncio.run(bot_main(token, log_queue)))
    process.start()

def stop_bot():
    global process
    if process:
        process.terminate()
        process = None

def reload_cog(cog_name):
    global bot
    if bot:
        try:
            asyncio.run_coroutine_threadsafe(bot.reload_extension(f"cogs.{cog_name}"), bot.loop)
        except Exception as e:
            raise Exception(f"Failed to reload cog {cog_name}: {str(e)}")