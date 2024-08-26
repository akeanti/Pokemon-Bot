import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta

# Define user economy data
user_data = {}

# Define item prices
item_prices = {
    "Pokéball": 100,
    "Potion": 50,
    "Revive": 200,
    "Bulbasaur": 500,
    "Charmander": 600,
    "Squirtle": 700
}

# Define custom emojis
currency_emoji = "<:currency:1277296037744349265>"

# Define Pokémon quiz questions and answers
quiz_questions = [
    {
        "question": "What is the evolved form of Charmander?",
        "options": ["Charmeleon", "Charizard", "Charbreeze"],
        "answer": "Charizard"
    },
    {
        "question": "Which Pokémon evolves into Pikachu?",
        "options": ["Pichu", "Raichu", "Sandshrew"],
        "answer": "Pichu"
    },
    {
        "question": "What type is Bulbasaur?",
        "options": ["Grass/Poison", "Fire/Flying", "Water"],
        "answer": "Grass/Poison"
    },
    # Add more questions up to 30
]


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.active_events = {}
        self.current_event_message = None

    @app_commands.command(name="event",
                          description="Join a special Pokémon event")
    async def event(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = discord.utils.utcnow()

        # Check if the user has participated today
        if user_id in self.active_events and self.active_events[
                user_id] > current_time:
            time_left = self.active_events[user_id] - current_time
            minutes, seconds = divmod(int(time_left.total_seconds()), 60)
            await interaction.response.send_message(
                f"You can participate in another event in {minutes}m {seconds}s.",
                ephemeral=False)
            return

        # Choose a random question
        question = random.choice(quiz_questions)
        options = "\n".join([
            f"{i+1}. {option}" for i, option in enumerate(question["options"])
        ])
        embed = discord.Embed(
            title="Pokémon Quiz Event",
            description=f"{question['question']}\n\n{options}",
            color=discord.Color.blue())

        # Save the question and correct answer
        self.active_events[user_id] = current_time + timedelta(days=1)
        self.current_event_message = await interaction.response.send_message(
            embed=embed)

        # Wait for the user's response
        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            if msg.content.isdigit():
                answer_index = int(msg.content) - 1
                if 0 <= answer_index < len(question["options"]):
                    answer = question["options"][answer_index]
                    if answer == question["answer"]:
                        # Correct answer
                        user_data.setdefault(
                            user_id, {})['balance'] = user_data.get(
                                user_id, {}).get('balance', 0) + 100
                        result_embed = discord.Embed(
                            title="Correct Answer!",
                            description=
                            f"Congratulations {interaction.user.mention}! You've earned 100 {currency_emoji}.",
                            color=discord.Color.green())
                    else:
                        # Incorrect answer
                        result_embed = discord.Embed(
                            title="Incorrect Answer!",
                            description=
                            "Sorry, that's not correct. The event has ended.",
                            color=discord.Color.red())
                        self.current_event_message = None
                else:
                    # Invalid answer index
                    result_embed = discord.Embed(
                        title="Invalid Option!",
                        description=
                        "The option you selected is not valid. Please try again.",
                        color=discord.Color.red())
                    self.current_event_message = None
            else:
                # Non-digit input
                result_embed = discord.Embed(
                    title="Invalid Input!",
                    description="Please enter a valid option number.",
                    color=discord.Color.red())
                self.current_event_message = None

            await self.current_event_message.edit(
                embed=result_embed
            ) if self.current_event_message else await interaction.followup.send(
                embed=result_embed)

        except asyncio.TimeoutError:
            # Timeout
            timeout_embed = discord.Embed(
                title="Time's Up!",
                description=
                "You took too long to answer. Please try the event again.",
                color=discord.Color.red())
            await self.current_event_message.edit(
                embed=timeout_embed
            ) if self.current_event_message else await interaction.followup.send(
                embed=timeout_embed)
            self.current_event_message = None


async def setup(bot):
    await bot.add_cog(Events(bot))
