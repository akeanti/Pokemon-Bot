import discord
from discord import app_commands
from discord.ext import commands
import random


class Games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pokemon_quiz",
                          description="Take a Pokémon quiz!")
    async def pokemon_quiz(self, interaction: discord.Interaction):
        questions = [
            ("What is Pikachu's type?", ["Electric", "Water", "Fire"]),
            ("Which Pokémon is #001 in the Pokédex?",
             ["Bulbasaur", "Charmander", "Squirtle"]),
        ]
        question, answers = random.choice(questions)
        await interaction.response.send_message(
            f"Quiz: {question}\nOptions: {', '.join(answers)}")


async def setup(bot):
    await bot.add_cog(Games(bot))
