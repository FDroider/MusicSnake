import os
import disnake
import logging
from dotenv import load_dotenv, find_dotenv
from disnake.ext import commands

# Создано Droid-Android

logger = logging.getLogger("disnake")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="MusicBot.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

Prefix = '!'
intents = disnake.Intents.all()
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(command_prefix=Prefix, intents=intents, command_sync_flags=command_sync_flags)


@bot.slash_command(description="Загрузить cog")
@commands.is_owner()
async def load_cog(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.response.send_message("Cog загружен", ephemeral=True, delete_after=10)


@bot.slash_command(description="Выгрузить cog")
@commands.is_owner()
async def unload_cog(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.response.send_message("Cog выгружен", ephemeral=True, delete_after=10)


@bot.slash_command(description="Перезагрузить cog")
@commands.is_owner()
async def reload_cog(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")
    await ctx.response.send_message("Cog перезагужен", ephemeral=True, delete_after=10)


@bot.slash_command()
@commands.is_owner()
async def reload_locale(ctx):
    bot.i18n.reload()
    await ctx.response.send_message("Локализация перезагружена", ephemeral=True)


@bot.slash_command()
@commands.is_owner()
async def load_locale(ctx, file):
    bot.i18n.load(f"locale/{file}")
    await ctx.response.send_message("Локализация загружена", ephemeral=True)

for filename in os.listdir("cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

for filename in os.listdir("locale"):
    if filename.endswith(".json"):
        bot.i18n.load(f"locale/{filename}")

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    bot.run(os.environ["TOKEN_API"])
