import discord
from discord import app_commands
from discord.ext import commands


class Achievements(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # Example achievements (you can modify or expand this)
        self.achievements = {
            1: {
                "name": "Pokémon Master",
                "description": "Catch 100 Pokémon",
                "image": "https://example.com/pokemon_master.png"
            },
            2: {
                "name": "Champion",
                "description": "Win 50 battles",
                "image": "https://example.com/champion.png"
            },
            3: {
                "name": "Collector",
                "description": "Collect 50 cards",
                "image": "https://example.com/collector.png"
            }
        }
        self.user_achievements = {}

    @app_commands.command(name="view_achievements",
                          description="View your achievements")
    async def view_achievements(self, interaction: discord.Interaction):
        user_achievements = self.user_achievements.get(interaction.user.id, [])

        if user_achievements:
            embed = discord.Embed(
                title=f"{interaction.user.name}'s Achievements",
                color=discord.Color.blue())
            for achievement_id in user_achievements:
                achievement = self.achievements.get(achievement_id)
                embed.add_field(name=achievement['name'],
                                value=achievement['description'],
                                inline=False)
                embed.set_thumbnail(url=achievement['image'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="No Achievements",
                description="You haven't unlocked any achievements yet!",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unlock_achievement",
                          description="Unlock a specific achievement")
    async def unlock_achievement(self, interaction: discord.Interaction,
                                 achievement_id: int):
        if achievement_id not in self.achievements:
            await interaction.response.send_message(
                "This achievement does not exist.", ephemeral=True)
            return

        self.user_achievements.setdefault(interaction.user.id,
                                          []).append(achievement_id)
        achievement = self.achievements[achievement_id]

        embed = discord.Embed(
            title="Achievement Unlocked!",
            description=
            f"You unlocked the **{achievement['name']}** achievement!",
            color=discord.Color.gold())
        embed.set_image(url=achievement['image'])
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Achievements(bot))
