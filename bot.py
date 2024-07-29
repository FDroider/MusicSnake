import os
import disnake
import logging
from dotenv import load_dotenv, find_dotenv
from disnake.ext import commands

# Made Droid-Android

Prefix = '!'
intents = disnake.Intents.all()
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.InteractionBot(intents=intents, command_sync_flags=command_sync_flags)


async def i18n_emb_message(ctx, title_key, desc_key, title_extra="", desc_extra="",
                           colour: disnake.Colour = disnake.Colour.default(), response: bool = False,
                           delete_after: int = ..., ephemeral: bool = False):
    local_user = str(ctx.locale)
    if local_user not in ("ru", "uk", "en-US"):
        local_user = "en-US"

    emb = disnake.Embed(title=f"{bot.i18n.get(key=title_key)[local_user]} {title_extra}" if title_key else None,
                        description=f"{bot.i18n.get(key=desc_key)[local_user]} {desc_extra}" if desc_key else None,
                        colour=colour)
    if response:
        return await ctx.response.send_message(embed=emb, delete_after=delete_after, ephemeral=ephemeral)
    return await ctx.followup.send(embed=emb, delete_after=delete_after, ephemeral=ephemeral)


async def i18n_message(ctx, key: str, delete_after: int = ..., ephemeral: bool = False):
    local_user = str(ctx.locale)
    if local_user not in ("ru", "uk", "en-US"):
        local_user = "en-US"

    return await ctx.send(bot.i18n.get(key=key)[local_user], delete_after=delete_after, ephemeral=ephemeral)


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
        if filename.startswith("creator"):
            continue
        bot.load_extension(f"cogs.{filename[:-3]}")

for filename in os.listdir("locale"):
    if filename.endswith(".json"):
        bot.i18n.load(f"locale/{filename}")

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    bot.run(os.environ["TOKEN_API"])
