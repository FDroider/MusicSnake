import sqlite3
import disnake
from disnake.ext import commands
#from googletrans import Translator


class UserCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect('warn.db')
        self.cour = self.db.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=disnake.Status.online, activity=disnake.Game('Музыку /help'))
        print(f"{self.bot.user} only")
        self.cour.execute("""CREATE TABLE IF NOT EXISTS users(
            id INT,
            name TEXT,
            warns INT,
            count INT)""")
        self.db.commit()

        # print(self.bot.guilds)

        for guild in self.bot.guilds:
            for member in guild.members:
                if self.cour.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                    self.cour.execute(f'INSERT INTO users VALUES ({member.id}, "{member}", 0, 0)')
                    self.db.commit()
                else:
                    pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)

        if isinstance(error, commands.CommandNotFound):
            emb = disnake.Embed(title='Команда не найдена!',
                                description='Хочу обратить внимание что команди уже давно пишутся через / (слеш)\n'
                                            '\nДля того что бы больше узнать о командах напишите /help',
                                colour=disnake.Colour.red())

            emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
            emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar)

            await ctx.send(embed=emb)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Канал в котором пользавател будет получать роль
        channel = disnake.utils.get(self.bot.get_all_channels(), name="общее")

        if self.cour.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
            self.cour.execute(f'INSERT INTO users VALUES ({member.id}, "{member}", 0)')
            self.db.commit()
        else:
            pass

        # Роль каторую будет получать пользаватель
        role = disnake.utils.get(member.guild.roles, id=1087681025511006268)

        await member.add_roles(role)

        await channel.send(
            embed=disnake.Embed(title='Приветствую', description=f'Пользаватель {member.name}, присойденился к нам!',
                                colour=disnake.Colour.green()))

    @commands.slash_command(description="Нашли ошибку? Уведомите нас")
    @commands.cooldown(1, 3)
    async def report(self, ctx, message: str):
        """
        Parameters
        ----------
        message: Напишите какая проблема возникла и после каких действий
        """

        my_channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=ctx.author.guild.id, name='fixed-bugs')

        member = disnake.utils.get(self.bot.get_all_members(), id=843213314163081237)

        emb = disnake.Embed(title='Жалоба', description=f'{message}', colour=disnake.Colour.red())

        emb.set_footer(text=f'Жалоба от пользавателя {ctx.author.name}#{ctx.author.discriminator}',
                       icon_url=ctx.author.avatar)

        await member.send(embed=emb)

        emb = disnake.Embed(title="Отправлено :white_check_mark:",
                            description=f"{ctx.author.name} ваш репорт отправлен моему разработчику на расмотрение "
                                        f"и последственое решение",
                            colour=disnake.Colour.green())

        emb.add_field(name="Уведомление о исправлениие ошибки",
                      value=f"Разработчик уведомит о исправлении ощибки в канале: {my_channel.mention}",
                      inline=False)

        await ctx.response.send_message(embed=emb)

    @commands.slash_command(description="Ваш счётчик предупреждений")
    async def my_warns(self, ctx):
        warns = self.cour.execute("SELECT warns FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]

        counter = self.cour.execute("SELECT count FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]

        emb = disnake.Embed(title="Предупреждения",
                            description=f'У тебя {warns} предупреждения',
                            color=disnake.Colour.gold())

        emb.add_field(name="Количество нарушений", value=f"У тебя {counter}")

        await ctx.response.send_message(embed=emb, ephemeral=True)

    @commands.slash_command(description="Просмотор счётчика предупреждений другого учасника")
    @commands.default_member_permissions(manage_permissions=True)
    async def warns(self, ctx, member: disnake.Member):
        """
        Parameters
        ----------
        member: Ник пользавателя
        """
        warns = self.cour.execute("SELECT warns FROM users WHERE id = {}".format(member.id)).fetchone()[0]

        counter = self.cour.execute("SELECT count FROM users WHERE id = {}".format(member.id)).fetchone()[0]

        emb = disnake.Embed(title="Предупреждения",
                            description=f'У пользавателя {member.name}, {warns} предупреждения',
                            color=disnake.Colour.gold())

        emb.add_field(name="Количенство нарушений", value=f"У пользавателя {member.name}, {counter} нарушений")

        await ctx.response.send_message(embed=emb, ephemeral=True)

    @commands.slash_command(description="Выдать предупреждение пользааваьелю")
    @commands.default_member_permissions(manage_permissions=True)
    async def add_warn(self, ctx, member: disnake.Member, ticket: int, reason: str = 'Не указана'):
        """
        Parameters
        ----------
        member: Ник пользавателя
        reason: Причина выдачи варна
        ticket: Количесто варнов которые будут выданы
        """

        if ticket < 0:
            self.cour.execute("UPDATE users SET warns = warns + {} WHERE id = {}".format(-ticket, member.id))
        else:
            self.cour.execute("UPDATE users SET warns = warns + {} WHERE id = {}".format(ticket, member.id))

        self.db.commit()

        emb = disnake.Embed(title="Пользавателю был выдан", description=f"{ctx.author.name} выдал варн/ны",
                            colour=disnake.Colour.dark_red())

        emb.add_field(name="Ник пользавателя которому выдан варн", value=f"{member.name}")
        emb.add_field(name="Причына выдачы варна", value=f"{reason}")
        emb.add_field(name="Колтчество варнов", value=f"{ticket}")

        await ctx.response.send_message(embed=emb)

    @commands.slash_command(description="Удалить предупреждение пользавателя")
    @commands.default_member_permissions(manage_permissions=True)
    async def del_warn(self, ctx, member: disnake.Member, ticket: int):
        """
        Parameters
        ----------
        member: Ник пользавателя
        ticket: Количесто варнов которые будут выданы
        """

        if ticket < 0:
            self.cour.execute("UPDATE users SET warns = warns + {} WHERE id = {}".format(ticket, member.id))
        else:
            self.cour.execute("UPDATE users SET warns = warns + {} WHERE id = {}".format(-ticket, member.id))

        warns = self.cour.execute("SELECT warns FROM users WHERE id = {}".format(member.id)).fetchone()[0]

        if warns < 0:
            self.cour.execute("UPDATE users SET warns = 0 WHERE id = {}".format(member.id))

        self.db.commit()

        if warns >= 0:
            emb = disnake.Embed(title="У пользавателя забрали варн", description=f"{ctx.author.name} забрал варн/ны",
                                colour=disnake.Colour.dark_red())

            emb.add_field(name="Ник пользавателя у которого забрали варн", value=f"{member.name}")
            emb.add_field(name="Колтчество забраних варнов", value=f"{-ticket}")

            await ctx.response.send_message(embed=emb)
        elif warns < 0:
            emb = disnake.Embed(title="Ошибка", description="У пользавателя нет варнов!",
                                colour=disnake.Colour.dark_red())

            await ctx.response.send_message(embed=emb, ephemeral=True)

    @commands.slash_command(description="Добавить нарушение")
    @commands.default_member_permissions(manage_guild=True)
    async def add_count(self, ctx, member: disnake.Member, ticket: int, reason: str = 'Не указана'):
        """
        Parameters
        ----------
        member: Ник пользавателя
        reason: Причина выдачи нарушения
        ticket: Количесто нарушений которые будут выданы
        """
        if ticket < 0:
            self.cour.execute("UPDATE users SET count = count + {} WHERE id = {}".format(-ticket, member.id))
        else:
            self.cour.execute("UPDATE users SET count = count + {} WHERE id = {}".format(ticket, member.id))

        self.db.commit()

        emb = disnake.Embed(title="Пользавателю была выдано нарушение", description=f"{ctx.author.name} выдал нарешения",
                            colour=disnake.Colour.dark_red())

        emb.add_field(name="Ник пользавателя которому выдан варн", value=f"{member.name}")
        emb.add_field(name="Причына выдачы нарушения", value=f"{reason}")
        emb.add_field(name="Колтчество нарушений", value=f"{ticket}")

        await ctx.response.send_message(embed=emb)

    @commands.slash_command(description="Удалить нарушения")
    @commands.default_member_permissions(manage_guild=True)
    async def del_count(self, ctx, member: disnake.Member, ticket: int):
        """
        Parameters
        ----------
        member: Ник пользавателя
        ticket: Количество нарушений которие будут удалены
        """
        if ticket < 0:
            self.cour.execute("UPDATE users SET count = count + {} WHERE id = {}".format(ticket, member.id))
        else:
            self.cour.execute("UPDATE users SET count = count + {} WHERE id = {}".format(-ticket, member.id))

        counter = self.cour.execute("SELECT count FROM users WHERE id = {}".format(member.id)).fetchone()[0]

        if counter < 0:
            self.cour.execute("UPDATE users SET count = 0 WHERE id = {}".format(member.id))

        self.db.commit()

        if counter >= 0:
            emb = disnake.Embed(title="У пользавателя забрали нарушение", description=f"{ctx.author.name} забрал нерушения",
                                colour=disnake.Colour.dark_red())

            emb.add_field(name="Ник пользавателя у которого забрали варн", value=f"{member.name}")
            emb.add_field(name="Колтчество забраних варнов", value=f"{-ticket}")

            await ctx.response.send_message(embed=emb)
        elif counter < 0:
            emb = disnake.Embed(title="Ошибка", description="У пользавателя нет нарушений!",
                                colour=disnake.Colour.dark_red())

            await ctx.response.send_message(embed=emb, ephemeral=True)

def setup(bot):
    bot.add_cog(UserCommand(bot))
