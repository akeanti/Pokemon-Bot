import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import random

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
pokeball_emoji = "<:pokeball:1277294164387827783>"
potion_emoji = "<:potion:1277295067660554403>"
revive_emoji = "<:revive:1277295634331861065>"
currency_emoji = "<:currency:1277296037744349265>"

# Define Pokémon emojis
bulbasaur_emoji = "<:bulbasaur:1277296809659596902>"
charmander_emoji = "<:charmander:1277296747823104000>"
squirtle_emoji = "<:squirtle:1277296695901687829>"


class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shop", description="View the Pokémon shop")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Pokémon Shop",
            description=
            "Welcome to the shop! Use the `/buy` command to purchase items.",
            color=discord.Color.blue())

        for item, price in item_prices.items():
            emoji = {
                "Pokéball": pokeball_emoji,
                "Potion": potion_emoji,
                "Revive": revive_emoji,
                "Bulbasaur": bulbasaur_emoji,
                "Charmander": charmander_emoji,
                "Squirtle": squirtle_emoji
            }.get(item, "")

            embed.add_field(name=f"{emoji} {item}",
                            value=f"Price: {price} {currency_emoji}",
                            inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy",
                          description="Purchase an item from the shop")
    async def buy(self, interaction: discord.Interaction, item: str):
        item = item.capitalize()  # Capitalize first letter to match item names

        if item not in item_prices:
            embed = discord.Embed(
                title="Error",
                description="Invalid item. Please check the shop with `/shop`.",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return

        user_id = interaction.user.id
        user_balance = user_data.get(user_id, {}).get('balance', 0)
        price = item_prices[item]

        if user_balance >= price:
            user_data.setdefault(user_id, {})['balance'] -= price
            embed = discord.Embed(title="Purchase Successful",
                                  description=f"You bought a {item}!",
                                  color=discord.Color.green())
        else:
            embed = discord.Embed(
                title="Purchase Failed",
                description=f"You don't have enough credits to buy a {item}.",
                color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="balance",
                          description="Check your current balance")
    async def balance(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        balance = user_data.get(user_id, {}).get('balance', 0)
        embed = discord.Embed(
            title="Balance",
            description=f"You have {balance} {currency_emoji}.",
            color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Work to earn credits")
    async def work(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if 'last_work' in user_data.get(user_id, {}):
            last_work_time = user_data[user_id]['last_work']
            if (discord.utils.utcnow() -
                    last_work_time).total_seconds() < 3600:  # 1 hour cooldown
                time_left = 3600 - (discord.utils.utcnow() -
                                    last_work_time).total_seconds()
                minutes, seconds = divmod(int(time_left), 60)
                embed = discord.Embed(
                    title="Cooldown",
                    description=f"You can work again in {minutes}m {seconds}s.",
                    color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)
                return

        # Random work event
        event, (min_earn, max_earn) = random.choice(work_events)
        earned = random.randint(min_earn, max_earn)
        user_data.setdefault(user_id, {})['balance'] = user_data.get(
            user_id, {}).get('balance', 0) + earned
        user_data[user_id]['last_work'] = discord.utils.utcnow()

        embed = discord.Embed(
            title="Work Successful",
            description=
            f"{event} {earned} {currency_emoji}! Your new balance is {user_data[user_id]['balance']} {currency_emoji}.",
            color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="gift",
                          description="Gift credits to another user")
    async def gift(self, interaction: discord.Interaction,
                   recipient: discord.User, amount: int):
        sender_id = interaction.user.id
        recipient_id = recipient.id

        if amount <= 0:
            embed = discord.Embed(
                title="Gift Failed",
                description="You cannot gift 0 or negative credits.",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return

        sender_balance = user_data.get(sender_id, {}).get('balance', 0)
        if sender_balance < amount:
            embed = discord.Embed(
                title="Gift Failed",
                description=
                "You don't have enough credits to gift this amount.",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return

        user_data.setdefault(sender_id, {})['balance'] -= amount
        user_data.setdefault(recipient_id, {})['balance'] = user_data.get(
            recipient_id, {}).get('balance', 0) + amount
        embed = discord.Embed(
            title="Gift Successful",
            description=
            f"You gifted {amount} {currency_emoji} to {recipient.mention}!",
            color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard",
                          description="View the top users by credits")
    async def leaderboard(self, interaction: discord.Interaction):
        sorted_users = sorted(user_data.items(),
                              key=lambda x: x[1].get('balance', 0),
                              reverse=True)
        top_users = sorted_users[:10]
        leaderboard = "\n".join([
            f"<@{user_id}>: {data.get('balance', 0)} {currency_emoji}"
            for user_id, data in top_users
        ])

        embed = discord.Embed(title="Leaderboard",
                              description=leaderboard or "No users found",
                              color=discord.Color.purple())
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Shop(bot))
