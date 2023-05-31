import asyncio
import disnake
from disnake.ext import commands
from disnake import TextInputStyle
from typing import Optional
from functools import lru_cache


voting_a = []
voting_d = []
author_id = []


class ButtonVote(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = Optional[bool]

    @disnake.ui.button(label="Да", style=disnake.ButtonStyle.green, custom_id='yes')
    async def accept(self, button: disnake.ui.Button, inter: disnake.Interaction):

        if inter.author.id in author_id:
            await inter.send(embed=disnake.Embed(title="Ошибка", description="Второй раз голосовать нельзя",
                                                 colour=disnake.Colour.red()),
                             ephemeral=True)
            return

        await inter.send("Вы проголосовали", ephemeral=True, delete_after=5)

        author_id.append(inter.author.id)
        voting_a.append(inter.author.name)

        self.value = True

    @disnake.ui.button(label="Нет", style=disnake.ButtonStyle.red, custom_id='no')
    async def against(self, button: disnake.ui.Button, inter: disnake.Interaction):

        if inter.author.id in author_id:
            await inter.send(embed=disnake.Embed(title="Ошибка", description="Второй раз голосовать нельзя",
                                                 colour=disnake.Colour.red()),
                             ephemeral=True)
            return

        await inter.send("Вы проголосовали", ephemeral=True, delete_after=5)

        author_id.append(inter.author.id)
        voting_d.append(inter.author.name)

        self.value = True


class ModelVote(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Название голосования",
                placeholder="Напишите название голосования",
                custom_id="Название",
                style=TextInputStyle.single_line,
                max_length=50
            ),

            disnake.ui.TextInput(
                label="Вопрос",
                placeholder="Введите вопрос",
                custom_id="Вопрос",
                style=TextInputStyle.paragraph,
                max_length=3000
            )
        ]
        super().__init__(
            title="Созданые голосования",
            custom_id="create_events",
            components=components,
        )


class ModelAnn(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Название об'явления",
                placeholder="Напишите название об'явления",
                custom_id="title",
                style=TextInputStyle.single_line,
                max_length=50
            ),

            disnake.ui.TextInput(
                label="Что будет в об'явлении",
                placeholder="Введите информацию которую хотите об'явить",
                custom_id="text",
                style=TextInputStyle.paragraph,
                max_length=3000
            ),
        ]
        super().__init__(
            title="Созданые голосования",
            custom_id="create_ann",
            components=components,
        )



@lru_cache(maxsize=None)
class CreateCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="vote")
    @commands.default_member_permissions(manage_events=True)
    async def create_voting(self, inter, time: int = None):
        """Создание голосования

        Parameters
        ----------
        time: Время проведения (в минутах)
        """
        await inter.response.send_modal(modal=ModelVote())

        await self.bot.wait_until_ready()

        if time is False:
            self.time_t = 600
        else:
            self.time_t = time * 10

    @commands.slash_command(name="announcements", description="Создание об'явлений")
    @commands.default_member_permissions(manage_events=True)
    async def create_announcement(self, inter, channel: disnake.TextChannel):
        """
        Parameters
        ----------
        channel: Канал в которий хотите отпраить об'явление
        """
        await inter.response.send_modal(modal=ModelAnn())

        self.channel = channel

    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction):

        if inter.custom_id == "create_ann":
            title = inter.text_values['title']
            text = inter.text_values['text']

            emb = disnake.Embed(title=f"{title}", description=f"@everyone {text}", colour=disnake.Colour.gold())

            await self.channel.send(embed=emb)
            await inter.send("Success", ephemeral=True, delete_after=2)

        if inter.custom_id == "create_events":
            voting_a.clear()
            voting_d.clear()
            author_id.clear()

            minutes = int((self.time_t // 60) % 60)
            seconds = int(self.time_t % 60)

            view = ButtonVote()
            title_text = inter.text_values["Название"]
            question_text = inter.text_values["Вопрос"]

            emb = disnake.Embed(title=f"{title_text}", description=f"{question_text}", colour=disnake.Colour.brand_green())

            emb.add_field(name="Время до окончания опроса", value=f"{minutes}:{seconds}")

            await inter.send(embed=emb, view=ButtonVote())

            while not minutes < 0 and not seconds < 0:
                seconds -= 1

                if seconds <= 0:
                    minutes -= 1
                    seconds = 59

                emb_e = disnake.Embed(title=f"{title_text}", description=f"{question_text}",
                                      colour=disnake.Colour.brand_green())

                emb_e.add_field(name="Время до окончания опроса", value=f"{minutes}:{seconds}")

                await inter.edit_original_message(embed=emb_e)

                await asyncio.sleep(1.15)

            emb = disnake.Embed(title="Голосование закончилось", description="Количество проголосовавших:",
                                colour=disnake.Colour.green())

            emb.add_field(name="За", value=f"{len(voting_a)}")
            emb.add_field(name="Против", value=f"{len(voting_d)}")

            await inter.send(embed=emb)


def setup(bot):
    bot.add_cog(CreateCommands(bot))