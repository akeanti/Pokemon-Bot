import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True


class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=
            None,  # No prefix since we're using only slash commands
            intents=intents,
            application_id=
            1277022737696690237  # Replace with your bot's Application ID
        )

    async def setup_hook(self):
        # Load all cogs
        initial_cogs = [
            'cogs.pokemon', 'cogs.cards', 'cogs.profile', 'cogs.achievements',
            'cogs.games', 'cogs.leaderboard', 'cogs.shop', 'cogs.events'
        ]

        for cog in initial_cogs:
            await self.load_extension(cog)

        # Sync all the slash commands
        await self.tree.sync()

    async def on_ready(self):
        # Print bot is running message
        print(f'{self.user} is now running!')

        # Set the bot's status
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.playing, name="Pokémon Adventures"))


bot = MyBot()

bot.run('BOT_TOKEN')
