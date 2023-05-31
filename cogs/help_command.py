import disnake
from disnake.ext import commands

Prefix1 = '/'


class HelpCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Помощь по командам")
    async def help(self, ctx):
        emb = disnake.Embed(title='Команды для управления', colour=disnake.Colour.light_gray())

        emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)

        emb.add_field(name='{}hello/hi'.format(Prefix1), value='Приветствие', inline=False)
        emb.add_field(name='{}play'.format(Prefix1), value='Воспроизводит музику из ютуба или youtube music',
                      inline=False)
        emb.add_field(name='{}volume'.format(Prefix1), value='Регулирует ргомкость музикы', inline=False)
        emb.add_field(name='{}leave'.format(Prefix1), value='Вийты из войса', inline=False)
        emb.add_field(name='{}random'.format(Prefix1), value='Рандомить число', inline=False)
        emb.add_field(name='{}chat'.format(Prefix1), value='Общайтесь с ботом, а точнее нейросетю', inline=False)
        emb.add_field(name='{}report'.format(Prefix1), value='Отправить отчёт об ошибке разработчику', inline=False)
        emb.add_field(name='{}my_warns'.format(Prefix1), value='Отправить отчёт об ошибке разработчику', inline=False)

        await ctx.response.send_message(embed=emb)

    @commands.slash_command(description="Помощь по командам для админов")
    @commands.default_member_permissions(manage_permissions=True, manage_roles=True)
    async def help_admin(self, ctx):
        emb = disnake.Embed(title='Команды для управления', colour=disnake.Colour.light_gray())

        emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)
        emb.add_field(name='{}clear'.format(Prefix1), value='Очистка чата', inline=False)
        emb.add_field(name='{}warns'.format(Prefix1), value='Посмотреть количество предупреждений пользавателя',
                      inline=False)

        emb.add_field(name='{}warn_user'.format(Prefix1), value='Выдать предупреждение пользавателю', inline=False)
        emb.add_field(name='{}del_warn'.format(Prefix1), value='Забрать предупреждение пользавателю', inline=False)

        await ctx.response.send_message(embed=emb)


def setup(bot):
    bot.add_cog(HelpCommands(bot))
