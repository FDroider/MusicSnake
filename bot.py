import os
import disnake
from disnake.ext import commands

#Create by Droid-Android

Prefix = '!'
intents = disnake.Intents.all()
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(command_prefix=Prefix, intents=intents, command_sync_flags=command_sync_flags)


@bot.slash_command(description="Загрузить cog")
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.response.send_message("Cog загружен", ephemeral=True, delete_after=10)


@bot.slash_command(description="Выгрузить cog")
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.response.send_message("Cog выгружен", ephemeral=True, delete_after=10)


@bot.slash_command(description="Перезагрузить cog")
@commands.is_owner()
async def reload(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")
    await ctx.response.send_message("Cog перезагужен", ephemeral=True, delete_after=10)


@load.error
async def load_errors(error, ctx):
    if isinstance(error, commands.NotOwner):
        await ctx.response.send_message("Ета команда не доступна по скольку вы не являетесь разработчиком",
                                        ephemeral=True,
                                        delete_after=5)


@unload.error
async def unload_errors(error, ctx):
    if isinstance(error, commands.NotOwner):
        await ctx.response.send_message("Ета команда не доступна по скольку вы не являетесь разработчиком",
                                        ephemeral=True,
                                        delete_after=5)


@reload.error
async def reload_errors(error, ctx):
    if isinstance(error, commands.NotOwner):
        await ctx.response.send_message("Ета команда не доступна по скольку вы не являетесь разработчиком",
                                        ephemeral=True,
                                        delete_after=5)

for filename in os.listdir("cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(os.environ["TOKEN_API"])