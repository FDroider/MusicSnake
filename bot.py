import os
import disnake
from dotenv import load_dotenv, find_dotenv
from disnake.ext import commands

# Made FDroider

intents = disnake.Intents.all()
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = False
bot = commands.InteractionBot(intents=intents, command_sync_flags=command_sync_flags)

def get_i18n_value(key, lang):
    try:
        return bot.i18n.get(key)[lang]
    except:
        return key

async def i18n_emb_message(ctx, title_key=False, desc_key=False, title_extra="", desc_extra="", author_text=None,
                           author_url=None, author_icon=None, footer_text=None, footer_icon=None,
                           colour: disnake.Colour = disnake.Colour.default(), response: bool = False,
                           delete_after: int = ..., ephemeral: bool = False):
    local_user = str(ctx.locale)

    if local_user not in ("ru", "uk", "en-US"):
        local_user = "en-US"

    if title_key or desc_key:
        emb = disnake.Embed(title=f"{get_i18n_value(title_key, local_user)} {title_extra}" if title_key else None,
                            description=f"{get_i18n_value(desc_key, local_user)} {desc_extra}" if desc_key else None,
                            colour=colour)
    else:
        emb = disnake.Embed(title=f"{title_extra}",
                            description=f"{desc_extra}",
                            colour=colour)
    if author_text or author_url or author_icon:
        emb.set_author(name=author_text if author_text else "",
                       url=author_url if author_url else None,
                       icon_url=author_icon if author_icon else None)
    emb.set_footer(text=footer_text if footer_text else "", icon_url=footer_icon)
    if delete_after == Ellipsis and not response:
        return await ctx.followup.send(embed=emb, ephemeral=ephemeral)
    elif delete_after == Ellipsis and response:
        return await ctx.response.send_message(embed=emb, ephemeral=ephemeral)
    elif delete_after != Ellipsis and response:
        return await ctx.response.send_message(embed=emb, delete_after=delete_after, ephemeral=ephemeral)
    return await ctx.followup.send(embed=emb, delete_after=delete_after, ephemeral=ephemeral)


async def i18n_message(ctx, key: str, delete_after: int = ..., ephemeral: bool = False):
    local_user = str(ctx.locale)
    if local_user not in ("ru", "uk", "en-US"):
        local_user = "en-US"

    return await ctx.send(get_i18n_value(key, local_user), delete_after=delete_after, ephemeral=ephemeral)


@bot.slash_command(description="Load cog")
@commands.is_owner()
async def load_cog(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.response.send_message("Cog loaded", ephemeral=True, delete_after=10)


@bot.slash_command(description="Unload cog")
@commands.is_owner()
async def unload_cog(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.response.send_message("Cog unloaded", ephemeral=True, delete_after=10)


@bot.slash_command(description="Reload cog")
@commands.is_owner()
async def reload_cog(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")
    await ctx.response.send_message("Cog reloaded", ephemeral=True, delete_after=10)


@bot.slash_command()
@commands.is_owner()
async def reload_locale(ctx):
    bot.i18n.reload()
    await ctx.response.send_message("Locales reloaded", ephemeral=True)


@bot.slash_command()
@commands.is_owner()
async def load_locale(ctx, file):
    bot.i18n.load(f"locale/{file}")
    await ctx.response.send_message("Locale loaded", ephemeral=True)


for filename in os.listdir("cogs"):
    try:
        if filename.endswith(".py"):
            if filename.startswith("creator"):
                continue
            bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded: {filename}")
    except Exception as e:
        print(f"Failed to load {filename}: {e}")

for filename in os.listdir("locale"):
    if filename.endswith(".json"):
        bot.i18n.load(f"locale/{filename}")
        print(f"Loaded locale: {filename}")

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    bot.run(os.environ["TOKEN_API"])
