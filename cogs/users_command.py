import sqlite3
import disnake
from disnake.ext import commands
from disnake import Localized
from random import choice


class UserCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.btn_list = ["/help", "/play", "/report"]
        self.db = sqlite3.connect('warn.db')
        self.db_ex = sqlite3.connect('except_user.db')
        self.cour = self.db.cursor()
        self.cour_ex = self.db_ex.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        # Изменяем статус бота на активный
        activity = disnake.Activity(name="music", type=disnake.ActivityType.listening)
        await self.bot.change_presence(status=disnake.Status.online, activity=activity)
        # Выводим сообщение что бот запущен
        print(f"{self.bot.user} only")
        # В базе данных SQL создаём таблицу со значения и их типами данных
        self.cour.execute("""CREATE TABLE IF NOT EXISTS users(
            id INT,
            name TEXT,
            warns INT,
            count INT)""")
        self.db.commit()

        self.cour_ex.execute("""CREATE TABLE IF NOT EXISTS exct(
            user INT,
            guild INT)""")
        self.db_ex.commit()

        # message = ("Вышло новое обновление\n"
        #            "========================="
        #            "\nВерсия: 1.6 beta\n"
        #            "\nСписок изменений:\n"
        #            "- Исправление багов\n"
        #            "- Добавлена локализация(частично): eng, ua, ru\n"
        #            "\nДля админов\n"
        #            "- Добавлени команды:\n"
        #            "\- except\n"
        #            "\- del-except\n"
        #            "\nВ будущем ожидается небольшой редизайн")
        #
        # channel = disnake.utils.get(self.bot.get_all_channels(), id=1097911609285951580)
        #
        # await channel.send(message)

        for guild in self.bot.guilds:
            for member in guild.members:
                if self.cour.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                    self.cour.execute(f'INSERT INTO users VALUES ({member.id}, "{member}", 0, 0)')
                    self.db.commit()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)

        if isinstance(error, commands.CommandNotFound):
            emb = disnake.Embed(title='Команда не найдена!',
                                description='Хочу обратить внимание что команди уже давно пишутся через / (слеш)\n'
                                            '\nДля того что бы больше узнать о командах напишите /help',
                                colour=disnake.Colour.red())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar)

            await ctx.send(embed=emb)

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        print(error)

        if isinstance(error, commands.CommandNotFound):
            emb = disnake.Embed(title='Команда не найдена!',
                                description=f'{ctx.author.content} Команда введена неверно. Что б узнать какие '
                                            f'есть команды напишыте /help', colour=disnake.Colour.red())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar)

            await ctx.send(embed=emb)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Канал в котором пользавател будет получать роль
        channel = disnake.utils.get(self.bot.get_all_channels(), name="общее")

        if self.cour.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
            self.cour.execute(f'INSERT INTO users VALUES ({member.id}, "{member}", 0, 0)')
            self.db.commit()

        # Роль каторую будет получать пользаватель
        role = disnake.utils.get(member.guild.roles, id=1087681025511006268)

        await member.add_roles(role)

        h_emb = disnake.Embed(title='Приветствую',
                              description=f'Пользаватель {member.global_name}, присойденился к нам!',
                              colour=disnake.Colour.green())

        h_emb1 = disnake.Embed(title="Привет", description="Добро пжаловать на сервер. "
                                                           "Если вдруг захочеш воспользаваться моими командами"
                                                           " напиши команду /help",
                               colour=disnake.Colour.green())

        await channel.send(embed=choice([h_emb, h_emb1]))

    @commands.slash_command(description=Localized(key="REPORT-COMMAND-DESCRIPTIONS"))
    @commands.cooldown(1, 1)
    async def report(self, ctx,
                     message: str = commands.param(
                         description=Localized(key="REPORT-COMMAND-DESCRIPTIONS_PARAMETERS-MESSAGE"))):
        #my_channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=ctx.author.guild.id, name='fixed-bugs')
        user_local = str(ctx.locale)
        member = disnake.utils.get(self.bot.get_all_members(), id=843213314163081237)

        emb = disnake.Embed(title='Жалоба', description=f'{message}', colour=disnake.Colour.red())

        emb.set_footer(text=f'Жалоба от пользавателя {ctx.author.global_name}',
                       icon_url=ctx.author.avatar)

        await member.send(embed=emb)

        if user_local == "ru":
            emb = disnake.Embed(title=f"{self.bot.i18n.get(key='REPORT-COMMAND_EMBED-TITLE')['ru']} :white_check_mark:",
                                description=f"{ctx.author.global_name} {self.bot.i18n.get(key='REPORT-COMMAND_EMBED-DESCRIPTION')['ru']}",
                                colour=disnake.Colour.green())

            await ctx.response.send_message(embed=emb)

        elif user_local == "uk" or user_local == "ua":
            emb = disnake.Embed(title=f"{self.bot.i18n.get(key='REPORT-COMMAND_EMBED-TITLE')['uk']} :white_check_mark:",
                                description=f"{ctx.author.global_name} {self.bot.i18n.get(key='REPORT-COMMAND_EMBED-DESCRIPTION')['uk']}",
                                colour=disnake.Colour.green())

            await ctx.response.send_message(embed=emb)

        else:
            emb = disnake.Embed(title=f"{self.bot.i18n.get(key='REPORT-COMMAND_EMBED-TITLE')['en-US']} :white_check_mark:",
                                description=f"{ctx.author.global_name} {self.bot.i18n.get(key='REPORT-COMMAND_EMBED-DESCRIPTION')['en-US']}",
                                colour=disnake.Colour.green())

            await ctx.response.send_message(embed=emb)

        # emb.add_field(name="Уведомление о исправлениие ошибки",
        #               value=f"Разработчик уведомит о исправлении ощибки в канале: {my_channel.mention}",
        #               inline=False)

    @commands.slash_command(description=Localized(key="MY-WARNS-COMMAND-DESCRIPTIONS"))
    async def my_warns(self, ctx):
        warns = self.cour.execute("SELECT warns FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]

        counter = self.cour.execute("SELECT count FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]

        user_local = str(ctx.locale)

        if user_local == "ru":
            emb = disnake.Embed(title=self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-TITLE")["ru"],
                                description=f'{self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-DESCRIPTION-PART1")["ru"]} {warns} '
                                            f'{self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-DESCRIPTION-PART2")["ru"]}',
                                color=disnake.Colour.gold())

            emb.add_field(name=self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-FIELD-NAME")["ru"],
                          value=f"{self.bot.i18n.get(key='MY-WARNS-COMMAND_EMBED-FIELD-VALUE')['ru']} {counter}")

            await ctx.response.send_message(embed=emb, ephemeral=True)

        elif user_local == "uk" or user_local == "ua":
            emb = disnake.Embed(title=self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-TITLE")["uk"],
                                description=f'{self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-DESCRIPTION-PART1")["uk"]} {warns} '
                                            f'{self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-DESCRIPTION-PART2")["uk"]}',
                                color=disnake.Colour.gold())

            emb.add_field(name=self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-FIELD-NAME")["uk"],
                          value=f"{self.bot.i18n.get(key='MY-WARNS-COMMAND_EMBED-FIELD-VALUE')['uk']} {counter}")

            await ctx.response.send_message(embed=emb, ephemeral=True)

        else:
            emb = disnake.Embed(title=self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-TITLE")["en-US"],
                                description=f'{self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-DESCRIPTION-PART1")["en-US"]} {warns} '
                                            f'{self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-DESCRIPTION-PART2")["en-US"]}',
                                color=disnake.Colour.gold())

            emb.add_field(name=self.bot.i18n.get(key="MY-WARNS-COMMAND_EMBED-FIELD-NAME")["en-US"],
                          value=f"{self.bot.i18n.get(key='MY-WARNS-COMMAND_EMBED-FIELD-VALUE')['en-US']} {counter}")

            await ctx.response.send_message(embed=emb, ephemeral=True)

    @commands.slash_command(description=Localized(key="WARNS-COMMAND-DESCRIPTIONS"))
    @commands.default_member_permissions(manage_permissions=True)
    async def warns(self, ctx,
                    member: disnake.Member = commands.param(
                        description=Localized(key="WARNS-COMMAND-DESCRIPTIONS_PARAMETERS"))):
        warns = self.cour.execute("SELECT warns FROM users WHERE id = {}".format(member.id)).fetchone()[0]

        counter = self.cour.execute("SELECT count FROM users WHERE id = {}".format(member.id)).fetchone()[0]

        user_local = str(ctx.locale)

        if user_local == "ru":
            emb = disnake.Embed(title=self.bot.i18n.get(key="WARNS-COMMAND_EMBED-TITLE")["ru"],
                                description=f'{self.bot.i18n.get(key="WARNS-COMMAND_EMBED-DESCRIPTION-PART1")["ru"]} {member.global_name}, '
                                            f'{warns} {self.bot.i18n.get(key="WARNS-COMMAND_EMBED-DESCRIPTION-PART2")["ru"]}',
                                color=disnake.Colour.gold())

            emb.add_field(name=self.bot.i18n.get(key="WARNS-COMMAND_EMBED-FIELD-NAME")["ru"],
                          value=f"{self.bot.i18n.get(key='WARNS-COMMAND_EMBED-FIELD-VALUE')['ru']} {counter}")

            await ctx.response.send_message(embed=emb, ephemeral=True)

        elif user_local == "uk" or user_local == "ua":
            emb = disnake.Embed(title=self.bot.i18n.get(key="WARNS-COMMAND_EMBED-TITLE")["uk"],
                                description=f'{self.bot.i18n.get(key="WARNS-COMMAND_EMBED-DESCRIPTION-PART1")["uk"]} {member.global_name}, '
                                            f'{warns} {self.bot.i18n.get(key="WARNS-COMMAND_EMBED-DESCRIPTION-PART2")["uk"]}',
                                color=disnake.Colour.gold())

            emb.add_field(name=self.bot.i18n.get(key="WARNS-COMMAND_EMBED-FIELD-NAME")["uk"],
                          value=f"{self.bot.i18n.get(key='WARNS-COMMAND_EMBED-FIELD-VALUE')['uk']} {counter}")

            await ctx.response.send_message(embed=emb, ephemeral=True)

        else:
            emb = disnake.Embed(title=self.bot.i18n.get(key="WARNS-COMMAND_EMBED-TITLE")["en-US"],
                                description=f'{self.bot.i18n.get(key="WARNS-COMMAND_EMBED-DESCRIPTION-PART1")["en-US"]} {member.global_name}, '
                                            f'{warns} {self.bot.i18n.get(key="WARNS-COMMAND_EMBED-DESCRIPTION-PART2")["en-US"]}',
                                color=disnake.Colour.gold())

            emb.add_field(name=self.bot.i18n.get(key="WARNS-COMMAND_EMBED-FIELD-NAME")["en-US"],
                          value=f"{self.bot.i18n.get(key='WARNS-COMMAND_EMBED-FIELD-VALUE')['en-US']} {counter}")

            await ctx.response.send_message(embed=emb, ephemeral=True)

    @commands.slash_command(description=Localized(key="ADD-WARN-DESCRIPTIONS"))
    @commands.default_member_permissions(manage_permissions=True)
    async def add_warn(self, ctx,
                       member: disnake.Member = commands.param(
                           description=Localized(key="ADD-WARN-DESCRIPTIONS_PARAMETERS-MEMBER")),
                       ticket: int = commands.param(default=1, description=Localized(
                           key="ADD-WARN-DESCRIPTIONS_PARAMETERS-TICKET")),
                       reason: str = commands.param(default='Не указана', description=Localized(
                           key="ADD-WARN-DESCRIPTIONS_PARAMETERS-REASON"))):
        if ticket < 0:
            self.cour.execute("UPDATE users SET warns = warns + {} WHERE id = {}".format(-ticket, member.id))
        else:
            self.cour.execute("UPDATE users SET warns = warns + {} WHERE id = {}".format(ticket, member.id))

        self.db.commit()

        user_local = str(ctx.locale)

        if user_local == "ru":
            emb = disnake.Embed(title=self.bot.i18n.get(key="ADD-WARM_EMBED-TITLE")["ru"],
                                description=f"{ctx.author.global_name} {self.bot.i18n.get(key='ADD-WARN_EMBED-DESCRIPTION')['ru']}",
                                colour=disnake.Colour.dark_red())

            emb.add_field(name=self.bot.i18n.get(key="ADD-WARN_EMBED-FIELD1-NAME")["ru"], value=f"{member.display_name}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-WARN_EMBED-FIELD2-NAME")["ru"], value=f"{reason}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-WARN_EMBED-FIELD3-NAME")["ru"], value=f"{ticket}")

            await ctx.response.send_message(embed=emb)

        elif user_local == "uk" or user_local == "ua":
            emb = disnake.Embed(title=self.bot.i18n.get(key="ADD-WARM_EMBED-TITLE")["uk"],
                                description=f"{ctx.author.global_name} {self.bot.i18n.get(key='ADD-WARN_EMBED-DESCRIPTION')['uk']}",
                                colour=disnake.Colour.dark_red())

            emb.add_field(name=self.bot.i18n.get(key="ADD-WARN_EMBED-FIELD1-NAME")["uk"], value=f"{member.display_name}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-WARN_EMBED-FIELD2-NAME")["uk"], value=f"{reason}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-WARN_EMBED-FIELD3-NAME")["uk"], value=f"{ticket}")

            await ctx.response.send_message(embed=emb)

        else:
            emb = disnake.Embed(title=self.bot.i18n.get(key="ADD-WARM_EMBED-TITLE")["en-US"],
                                description=f"{ctx.author.global_name} {self.bot.i18n.get(key='ADD-WARN_EMBED-DESCRIPTION')['en-US']}",
                                colour=disnake.Colour.dark_red())

            emb.add_field(name=self.bot.i18n.get(key="ADD-WARN_EMBED-FIELD1-NAME")["en-US"], value=f"{member.display_name}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-WARN_EMBED-FIELD2-NAME")["en-US"], value=f"{reason}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-WARN_EMBED-FIELD3-NAME")["en-US"], value=f"{ticket}")

            await ctx.response.send_message(embed=emb)

    @commands.slash_command(description=Localized(key="DEL-WARN-DESCRIPTIONS"))
    @commands.default_member_permissions(manage_permissions=True)
    async def del_warn(self, ctx,
                       member: disnake.Member = commands.param(
                           description=Localized(key="DEL-WARN-DESCRIPTIONS_PARAMETERS-MEMBER")),
                       ticket: int = commands.param(
                           description=Localized(key="DEL-WARN-DESCRIPTIONS_PARAMETERS-TICKET"))):
        if ticket < 0:
            self.cour.execute("UPDATE users SET warns = warns + {} WHERE id = {}".format(ticket, member.id))
        else:
            self.cour.execute("UPDATE users SET warns = warns + {} WHERE id = {}".format(-ticket, member.id))

        warns = self.cour.execute("SELECT warns FROM users WHERE id = {}".format(member.id)).fetchone()[0]

        user_local = str(ctx.locale)
        if warns < 0:
            self.cour.execute("UPDATE users SET warns = 0 WHERE id = {}".format(member.id))

        self.db.commit()

        if warns >= 0:
            if user_local == "ru":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-WARN-SUCCESS_EMBED-TITLE")["ru"],
                                    description=f"{ctx.author.global_name} "
                                                f"{self.bot.i18n.get(key='DEL-WARN-SUCCESS_EMBED-DESCRIPTION')['ru']}",
                                    colour=disnake.Colour.dark_red())

                emb.add_field(name=self.bot.i18n.get(key="DEL-WARN-SUCCESS_EMBED-FIELD1-NAME")["ru"],
                              value=f"{member.display_name}")
                emb.add_field(name=self.bot.i18n.get(key="DEL-WARN-SUCCESS_EMBED-FIELD2-NAME")["ru"],
                              value=f"{-ticket}")

                await ctx.response.send_message(embed=emb)

            elif user_local == "uk" or user_local == "ua":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-WARN-SUCCESS_EMBED-TITLE")["uk"],
                                    description=f"{ctx.author.global_name} "
                                                f"{self.bot.i18n.get(key='DEL-WARN-SUCCESS_EMBED-DESCRIPTION')['uk']}",
                                    colour=disnake.Colour.dark_red())

                emb.add_field(name=self.bot.i18n.get(key="DEL-WARN-SUCCESS_EMBED-FIELD1-NAME")["uk"],
                              value=f"{member.display_name}")
                emb.add_field(name=self.bot.i18n.get(key="DEL-WARN-SUCCESS_EMBED-FIELD2-NAME")["uk"],
                              value=f"{-ticket}")

                await ctx.response.send_message(embed=emb)

            else:
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-WARN-SUCCESS_EMBED-TITLE")["en-US"],
                                    description=f"{ctx.author.global_name} "
                                                f"{self.bot.i18n.get(key='DEL-WARN-SUCCESS_EMBED-DESCRIPTION')['en-US']}",
                                    colour=disnake.Colour.dark_red())

                emb.add_field(name=self.bot.i18n.get(key="DEL-WARN-SUCCESS_EMBED-FIELD1-NAME")["en-US"],
                              value=f"{member.display_name}")
                emb.add_field(name=self.bot.i18n.get(key="DEL-WARN-SUCCESS_EMBED-FIELD2-NAME")["en-US"],
                              value=f"{-ticket}")

                await ctx.response.send_message(embed=emb)

        elif warns < 0:
            if user_local == "ru":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-WARN-ERROR_EMBED-TITLE")["ru"],
                                    description=self.bot.i18n.get(key="DEL-WARN-ERROR_EMBED-DESCRIPTION")["ru"],
                                    colour=disnake.Colour.dark_red())

                await ctx.response.send_message(embed=emb, ephemeral=True)

            elif user_local == "uk" or user_local == "ua":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-WARN-ERROR_EMBED-TITLE")["uk"],
                                    description=self.bot.i18n.get(key="DEL-WARN-ERROR_EMBED-DESCRIPTION")["uk"],
                                    colour=disnake.Colour.dark_red())

                await ctx.response.send_message(embed=emb, ephemeral=True)

            else:
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-WARN-ERROR_EMBED-TITLE")["en-US"],
                                    description=self.bot.i18n.get(key="DEL-WARN-ERROR_EMBED-DESCRIPTION")["en-US"],
                                    colour=disnake.Colour.dark_red())

                await ctx.response.send_message(embed=emb, ephemeral=True)

    @commands.slash_command(description=Localized(key="ADD-COUNT-DESCRIPTIONS"))
    @commands.default_member_permissions(manage_guild=True)
    async def add_count(self, ctx,
                        member: disnake.Member = commands.param(
                            description=Localized(key="ADD-COUNT-DESCRIPTIONS_PARAMETERS-MEMBER")),
                        ticket: int = commands.param(
                            description=Localized(key="ADD-COUNT-DESCRIPTIONS_PARAMETERS-TICKET")),
                        reason: str = commands.param(
                            description=Localized(key="ADD-COUNT-DESCRIPTIONS_PARAMETERS-REASON"))):
        if ticket < 0:
            self.cour.execute("UPDATE users SET count = count + {} WHERE id = {}".format(-ticket, member.id))
        else:
            self.cour.execute("UPDATE users SET count = count + {} WHERE id = {}".format(ticket, member.id))

        self.db.commit()

        user_local = str(ctx.locale)

        if user_local == "ru":
            emb = disnake.Embed(title=self.bot.i18n.get(key="ADD-COUNT_EMBED-TITLE")["ru"],
                                description=f"{ctx.author.global_name} "
                                            f"{self.bot.i18n.get(key='ADD-COUNT_EMBED-DESCRIPTION')['ru']}",
                                colour=disnake.Colour.dark_red())

            emb.add_field(name=self.bot.i18n.get(key="ADD-COUNT_EMBED-FIELD1-NAME")["ru"], value=f"{member.display_name}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-COUNT_EMBED-FIELD2-NAME")["ru"], value=f"{reason}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-COUNT_EMBED-FIELD3-NAME")["ru"], value=f"{ticket}")

            await ctx.response.send_message(embed=emb)

        elif user_local == "uk" or user_local == "ua":
            emb = disnake.Embed(title=self.bot.i18n.get(key="ADD-COUNT_EMBED-TITLE")["uk"],
                                description=f"{ctx.author.global_name} "
                                            f"{self.bot.i18n.get(key='ADD-COUNT_EMBED-DESCRIPTION')['uk']}",
                                colour=disnake.Colour.dark_red())

            emb.add_field(name=self.bot.i18n.get(key="ADD-COUNT_EMBED-FIELD1-NAME")["uk"], value=f"{member.display_name}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-COUNT_EMBED-FIELD2-NAME")["uk"], value=f"{reason}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-COUNT_EMBED-FIELD3-NAME")["uk"], value=f"{ticket}")

            await ctx.response.send_message(embed=emb)

        else:
            emb = disnake.Embed(title=self.bot.i18n.get(key="ADD-COUNT_EMBED-TITLE")["en-US"],
                                description=f"{ctx.author.global_name} "
                                            f"{self.bot.i18n.get(key='ADD-COUNT_EMBED-DESCRIPTION')['en-US']}",
                                colour=disnake.Colour.dark_red())

            emb.add_field(name=self.bot.i18n.get(key="ADD-COUNT_EMBED-FIELD1-NAME")["en-US"], value=f"{member.display_name}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-COUNT_EMBED-FIELD2-NAME")["en-US"], value=f"{reason}")
            emb.add_field(name=self.bot.i18n.get(key="ADD-COUNT_EMBED-FIELD3-NAME")["en-US"], value=f"{ticket}")

            await ctx.response.send_message(embed=emb)

    @commands.slash_command(description=Localized(key="DEL-COUNT-DESCRIPTIONS"))
    @commands.default_member_permissions(manage_guild=True)
    async def del_count(self, ctx,
                        member: disnake.Member = commands.param(
                            description=Localized(key="DEL-COUNT-DESCRIPTIONS_PARAMETERS-MEMBER")),
                        ticket: int = commands.param(
                            description=Localized(key="DEL-COUNT-DESCRIPTIONS_PARAMETERS-TICKET"))):
        if ticket < 0:
            self.cour.execute("UPDATE users SET count = count + {} WHERE id = {}".format(ticket, member.id))
        else:
            self.cour.execute("UPDATE users SET count = count + {} WHERE id = {}".format(-ticket, member.id))

        counter = self.cour.execute("SELECT count FROM users WHERE id = {}".format(member.id)).fetchone()[0]

        if counter < 0:
            self.cour.execute("UPDATE users SET count = 0 WHERE id = {}".format(member.id))

        self.db.commit()

        user_local = str(ctx.locale)

        if counter >= 0:
            if user_local == "ru":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-COUNT-SUCCESS_EMBED-TITLE")["ru"],
                                    description=f"{ctx.author.global_name} "
                                                f"{self.bot.i18n.get(key='DEL-COUNT-SUCCESS_EMBED-DESCRIPTION')['ru']}",
                                    colour=disnake.Colour.dark_red())

                emb.add_field(name=self.bot.i18n.get(key="DEL-COUNT-SUCCESS_EMBED-FIELD1-NAME")["ru"],
                              value=f"{member.display_name}")
                emb.add_field(name=self.bot.i18n.get(key="DEL-COUNT-SUCCESS_EMBED-FIELD2-NAME")["ru"],
                              value=f"{-ticket}")

                await ctx.response.send_message(embed=emb)

            elif user_local == "uk" or user_local == "ua":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-COUNT-SUCCESS_EMBED-TITLE")["uk"],
                                    description=f"{ctx.author.global_name} "
                                                f"{self.bot.i18n.get(key='DEL-COUNT-SUCCESS_EMBED-DESCRIPTION')['uk']}",
                                    colour=disnake.Colour.dark_red())

                emb.add_field(name=self.bot.i18n.get(key="DEL-COUNT-SUCCESS_EMBED-FIELD1-NAME")["uk"],
                              value=f"{member.display_name}")
                emb.add_field(name=self.bot.i18n.get(key="DEL-COUNT-SUCCESS_EMBED-FIELD2-NAME")["uk"],
                              value=f"{-ticket}")

                await ctx.response.send_message(embed=emb)

            else:
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-COUNT-SUCCESS_EMBED-TITLE")["en-US"],
                                    description=f"{ctx.author.global_name} "
                                                f"{self.bot.i18n.get(key='DEL-COUNT-SUCCESS_EMBED-DESCRIPTION')['en-US']}",
                                    colour=disnake.Colour.dark_red())

                emb.add_field(name=self.bot.i18n.get(key="DEL-COUNT-SUCCESS_EMBED-FIELD1-NAME")["en-US"],
                              value=f"{member.display_name}")
                emb.add_field(name=self.bot.i18n.get(key="DEL-COUNT-SUCCESS_EMBED-FIELD2-NAME")["en-US"],
                              value=f"{-ticket}")

                await ctx.response.send_message(embed=emb)
        elif counter < 0:
            if user_local == "ru":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-COUNT-ERROR_EMBED-TITLE")[""],
                                    description=self.bot.i18n.get(key="DEL-COUNT-ERROR_EMBED-DESCRIPTION")[""],
                                    colour=disnake.Colour.dark_red())

                await ctx.response.send_message(embed=emb, ephemeral=True)

            elif user_local == "uk" or user_local == "ua":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-COUNT-ERROR_EMBED-TITLE")[""],
                                    description=self.bot.i18n.get(key="DEL-COUNT-ERROR_EMBED-DESCRIPTION")[""],
                                    colour=disnake.Colour.dark_red())

                await ctx.response.send_message(embed=emb, ephemeral=True)

            else:
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-COUNT-ERROR_EMBED-TITLE")[""],
                                    description=self.bot.i18n.get(key="DEL-COUNT-ERROR_EMBED-DESCRIPTION")[""],
                                    colour=disnake.Colour.dark_red())

                await ctx.response.send_message(embed=emb, ephemeral=True)


def setup(bot):
    bot.add_cog(UserCommand(bot))
