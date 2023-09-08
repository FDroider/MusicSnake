import disnake
import openai
from os import environ
from dotenv import load_dotenv, find_dotenv
from disnake import Localized
from disnake.ext import commands


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv(find_dotenv())
        # Ключ API от openai
        openai.api_key = environ["GPT_API"]

    @commands.slash_command(name='chat-gpt', description=Localized(key="GPT-COMMAND-DESCRIPTIONS"))
    async def chat_bot(self, ctx, prompt: str = commands.param(description=Localized(key="GPT-COMMAND-DESCRIPTIONS_PARAMETERS"))):

        await ctx.response.defer()

        # Получение сообщения
        def update(messages, role, content):
            messages.append({"role": role, "content": content})
            return messages

        # Получение ответа от chat-gpt
        def get_response(messages):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response["choices"][0]["message"]["content"]

        messages = [
            {"role": "system", "content": "You are a professional programmer on python"},
            {"role": "user", "content": "Hello. You must answer only on 1024 characters"}
        ]

        # try:
        while True:
            print(messages)
            user_input = prompt
            messages = update(messages, "user", user_input)
            model_response = get_response(messages)

            emb = disnake.Embed(title="Chat GPT ответил", description=f"```{model_response}```",
                                colour=disnake.Colour.green())

            await ctx.followup.send(embed=emb)
            return False
        # except:
        #     emb_err = disnake.Embed(title="Ошибка",
        #                             description="Нейросеть превысила допустимое количество символов "
        #                                         "для таких вопросов нужно идти нас сайт opanai https://chat.openai.com/",
        #                             colour=disnake.Colour.red())
        #
        #     await ctx.followup.send(embed=emb_err, ephemeral=True)


def setup(bot):
    bot.add_cog(Chat(bot))