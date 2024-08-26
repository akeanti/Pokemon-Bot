import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio


class Cards(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.user_cards = {}  # Stores cards for each user
        self.card_database = {
            "Blue-Eyes White Dragon": {
                "rarity":
                "Legendary",
                "image":
                "https://qph.cf2.quoracdn.net/main-qimg-98732885e1731509a4ce78d853dd0173-pjlq"
            },
            "Dark Magician": {
                "rarity":
                "Rare",
                "image":
                "https://qph.cf2.quoracdn.net/main-qimg-c1750fcd3e0aa30d9ea76d1dc12235cd"
            },
            "Dragon Master Knight": {
                "rarity":
                "Epic",
                "image":
                "https://qph.cf2.quoracdn.net/main-qimg-f46f34459bbe19e3840c264d306b7a56"
            },
            "Exodia the Forbidden One": {
                "rarity": "Mythical",
                "image":
                "https://example.com/exodia-image"  # Replace with a valid image URL
            },
            # Add more cards as needed
        }
        self.collect_cooldowns = {}  # Cooldown tracking

    @app_commands.command(name="collect",
                          description="Collect a new Yu-Gi-Oh! card")
    async def collect(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = asyncio.get_event_loop().time()

        # Check cooldown
        last_collect = self.collect_cooldowns.get(user_id, 0)
        if now - last_collect < 3600:  # 1 hour cooldown
            wait_time = int(3600 - (now - last_collect))
            await interaction.response.send_message(
                f"Please wait {wait_time // 60} minutes before collecting again."
            )
            return

        # Implement rare drop rate
        rare_cards = [
            card for card in self.card_database.keys()
            if self.card_database[card]["rarity"] == "Legendary"
        ]
        card_chance = 0.1 if random.random() < 0.1 else 0.3
        if random.random() < card_chance:  # Rare card drop chance
            card = random.choice(rare_cards)
        else:
            card = random.choice(list(self.card_database.keys()))

        self.user_cards.setdefault(user_id, []).append(card)
        self.collect_cooldowns[user_id] = now  # Update last collect time

        embed_color = self._get_embed_color(self.card_database[card]["rarity"])
        embed = discord.Embed(title="Card Collected!", color=embed_color)
        embed.add_field(name=card, value=self.card_database[card]["rarity"])
        embed.set_image(url=self.card_database[card]["image"])

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="show_cards",
                          description="Show your collected Yu-Gi-Oh! cards")
    async def show_cards(self, interaction: discord.Interaction):
        cards = self.user_cards.get(interaction.user.id, [])
        if cards:
            embeds = []
            for card in cards:
                rarity = self.card_database[card]["rarity"]
                embed_color = self._get_embed_color(rarity)
                embed = discord.Embed(title=card, color=embed_color)
                embed.add_field(name="Rarity", value=rarity, inline=False)
                embed.set_image(url=self.card_database[card]["image"])
                embeds.append(embed)

            # Send multiple embeds if necessary
            for embed in embeds:
                await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("You have no cards!")

    @app_commands.command(name="gift_card",
                          description="Gift a card to another user")
    async def gift_card(self, interaction: discord.Interaction,
                        recipient: discord.User, card_name: str):
        if card_name not in self.user_cards.get(interaction.user.id, []):
            await interaction.response.send_message("You don't own this card!")
            return

        self.user_cards[interaction.user.id].remove(card_name)
        self.user_cards.setdefault(recipient.id, []).append(card_name)
        await interaction.response.send_message(
            f"You gifted a {card_name} to {recipient.mention}!")

    @app_commands.command(name="exchange_card",
                          description="Exchange a card with another user")
    async def exchange_card(self, interaction: discord.Interaction,
                            recipient: discord.User, card_name: str):
        if card_name not in self.user_cards.get(interaction.user.id, []):
            await interaction.response.send_message("You don't own this card!")
            return

        if card_name not in self.user_cards.get(recipient.id, []):
            await interaction.response.send_message(
                f"{recipient.mention} doesn't own this card!")
            return

        self.user_cards[interaction.user.id].remove(card_name)
        self.user_cards[recipient.id].remove(card_name)
        self.user_cards[interaction.user.id].append(card_name)
        self.user_cards[recipient.id].append(card_name)
        await interaction.response.send_message(
            f"You exchanged a {card_name} with {recipient.mention}!")

    @app_commands.command(name="war",
                          description="Battle with your Yu-Gi-Oh! cards")
    async def battle(self, interaction: discord.Interaction,
                     opponent: discord.User):
        user_cards = self.user_cards.get(interaction.user.id, [])
        opponent_cards = self.user_cards.get(opponent.id, [])

        if not user_cards or not opponent_cards:
            await interaction.response.send_message(
                "Both you and your opponent need to have cards!")
            return

        user_card = random.choice(user_cards)
        opponent_card = random.choice(opponent_cards)

        user_rarity = self.card_database[user_card]["rarity"]
        opponent_rarity = self.card_database[opponent_card]["rarity"]

        win_message = "It's a tie!"
        if self._compare_rarities(user_rarity, opponent_rarity) > 0:
            win_message = "You won!"
        elif self._compare_rarities(user_rarity, opponent_rarity) < 0:
            win_message = f"{opponent.mention} won!"

        embed = discord.Embed(title="Battle Result",
                              color=discord.Color.purple())
        embed.add_field(name=f"Your Card: {user_card}",
                        value=user_rarity,
                        inline=True)
        embed.add_field(name=f"Opponent's Card: {opponent_card}",
                        value=opponent_rarity,
                        inline=True)
        embed.add_field(name="Result", value=win_message)

        await interaction.response.send_message(embed=embed)

    def _get_embed_color(self, rarity):
        colors = {
            "Legendary": discord.Color.gold(),
            "Epic": discord.Color.orange(),
            "Rare": discord.Color.blue(),
            "Mythical": discord.Color.purple(),
            "Unknown": discord.Color.default()
        }
        return colors.get(rarity, discord.Color.default())

    def _compare_rarities(self, rarity1, rarity2):
        rarity_order = {
            "Mythical": 4,
            "Legendary": 3,
            "Epic": 2,
            "Rare": 1,
            "Unknown": 0
        }
        return rarity_order.get(rarity1, 0) - rarity_order.get(rarity2, 0)


async def setup(bot):
    await bot.add_cog(Cards(bot))
