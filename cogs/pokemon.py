import discord
from discord import app_commands
from discord.ext import commands, tasks
import random


class Pokemon(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.pokemon_list = [{
            'name': 'Pikachu',
            'image': 'https://example.com/pikachu.png',
            'skill': 'Thunderbolt'
        }, {
            'name': 'Charmander',
            'image': 'https://example.com/charmander.png',
            'skill': 'Flamethrower'
        }, {
            'name': 'Squirtle',
            'image': 'https://example.com/squirtle.png',
            'skill': 'Water Gun'
        }, {
            'name': 'Bulbasaur',
            'image': 'https://example.com/bulbasaur.png',
            'skill': 'Vine Whip'
        }]
        self.user_pokemon = {}
        self.user_pokeballs = {}
        self.drop_pokemon.start()

    @app_commands.command(name="catch", description="Catch a wild Pokémon")
    async def catch(self, interaction: discord.Interaction):
        if self.user_pokeballs.get(interaction.user.id, 0) < 1:
            await interaction.response.send_message(
                "You don't have any Pokéballs! Earn more by chatting or completing challenges.",
                ephemeral=True)
            return

        pokemon = random.choice(self.pokemon_list)
        self.user_pokemon.setdefault(interaction.user.id, []).append(pokemon)
        self.user_pokeballs[interaction.user.id] -= 1

        embed = discord.Embed(title=f"A wild {pokemon['name']} appeared!",
                              description=f"You caught a {pokemon['name']}!",
                              color=discord.Color.green())
        embed.set_thumbnail(url=pokemon['image'])
        embed.add_field(name="Skill", value=pokemon['skill'], inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="battle",
        description="Challenge another trainer to a Pokémon battle")
    async def battle(self, interaction: discord.Interaction,
                     opponent: discord.Member):
        if not self.user_pokemon.get(interaction.user.id):
            await interaction.response.send_message(
                "You don't have any Pokémon! Catch one first.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Pokémon Battle!",
            description=
            f"{interaction.user.name} challenges {opponent.name} to a Pokémon battle!",
            color=discord.Color.blue())
        embed.set_thumbnail(url="https://example.com/battle.png")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="learn",
                          description="Teach your Pokémon a new skill")
    async def learn(self, interaction: discord.Interaction, pokemon_name: str,
                    new_skill: str):
        user_pokemon = self.user_pokemon.get(interaction.user.id, [])
        pokemon = next((p for p in user_pokemon
                        if p['name'].lower() == pokemon_name.lower()), None)

        if pokemon:
            pokemon['skill'] = new_skill
            embed = discord.Embed(
                title=f"{pokemon['name']} learned {new_skill}!",
                color=discord.Color.gold())
            embed.set_thumbnail(url=pokemon['image'])
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "You don't have that Pokémon.", ephemeral=True)

    @tasks.loop(minutes=10)  # Pokémon drop every 10 minutes
    async def drop_pokemon(self):
        channels = list(
            self.bot.get_all_channels())  # Convert generator to list
        if channels:
            channel = random.choice(channels)
            if isinstance(channel, discord.TextChannel):
                pokemon = random.choice(self.pokemon_list)
                embed = discord.Embed(
                    title="A wild Pokémon has appeared!",
                    description=
                    f"Type `/catch` to catch this wild {pokemon['name']}!",
                    color=discord.Color.orange())
                embed.set_thumbnail(url=pokemon['image'])
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            pokeballs = self.user_pokeballs.get(message.author.id, 0) + 1
            self.user_pokeballs[message.author.id] = pokeballs


async def setup(bot):
    await bot.add_cog(Pokemon(bot))
