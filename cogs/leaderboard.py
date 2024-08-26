import discord
from discord import app_commands
from discord.ext import commands


class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.leaderboard = {}

    @app_commands.command(name="show_leaderboard",
                          description="Show the global leaderboard")
    async def show_leaderboard(self, interaction: discord.Interaction):
        leaderboard_entries = sorted(self.leaderboard.items(),
                                     key=lambda x: x[1],
                                     reverse=True)
        if leaderboard_entries:
            leaderboard_message = "\n".join([
                f"{self.bot.get_user(user_id)}: {points} XP"
                for user_id, points in leaderboard_entries
            ])
            await interaction.response.send_message(
                f"Leaderboard:\n{leaderboard_message}")
        else:
            await interaction.response.send_message(
                "No leaderboard entries yet!")


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
