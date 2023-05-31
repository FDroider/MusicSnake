import disnake
import openai
from disnake.ext import commands
#from typing import List
#from googletrans import Translator
from config import api_key


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Ключ API от openai
        openai.api_key = api_key

    #@commands.command(aliases=['chat', 'чат'])
    @commands.slash_command(name='chat-gpt')
    async def chat_bot(self, ctx, prompt: str):
        """'Команда для общения с GPT-3.5'
        Parameters
        ----------
        prompt: Ваше сообщение которое будет отправлено GPT
        """

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

        try:
            while True:
                print(messages)
                user_input = prompt
                messages = update(messages, "user", user_input)
                model_response = get_response(messages)

                emb = disnake.Embed(title="Chat GPT ответил", description=f"```{model_response}```",
                                    colour=disnake.Colour.green())

                await ctx.followup.send(embed=emb)
                return False
        except:
            await ctx.followup.send(embed=disnake.Embed(title="Ошибка",
                                                        description="Нейросеть превысыла допустимое количество символов "
                                                                    "для таких вопросов нужно ити нас сайт opanai "
                                                                    "https://chat.openai.com/",
                                                        colour=disnake.Colour.red()), ephemeral=True)


def setup(bot):
    bot.add_cog(Chat(bot))