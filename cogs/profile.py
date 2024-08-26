import discord
from discord import app_commands
from discord.ext import commands


class Profile(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.profiles = {}

    @app_commands.command(name="set_profile",
                          description="Set your Pokémon profile")
    async def set_profile(self, interaction: discord.Interaction,
                          about_me: str):
        self.profiles[interaction.user.id] = about_me
        await interaction.response.send_message("Profile updated!")

    @app_commands.command(name="view_profile",
                          description="View your Pokémon profile")
    async def view_profile(self, interaction: discord.Interaction):
        profile = self.profiles.get(interaction.user.id, "No profile set.")
        await interaction.response.send_message(f"Your profile: {profile}")


async def setup(bot):
    await bot.add_cog(Profile(bot))
