import os
import json
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # Fetching the token from environment variables

# Setting Permissions
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable the members intent

# Set a Prefix for Commands
bot = commands.Bot(command_prefix='/', intents=intents)

# Dictionaries to store user XP, Aura balances, and levels per guild
user_experience = defaultdict(lambda: defaultdict(int))
user_aura = defaultdict(lambda: defaultdict(int))
user_levels = defaultdict(lambda: defaultdict(int))

# Load aura data from a file
def load_aura_data():
    try:
        with open('aura_data.json', 'r') as f:
            data = json.load(f)
            for guild_id, users in data.items():
                for user_id, aura in users.items():
                    user_aura[int(guild_id)][int(user_id)] = aura
    except FileNotFoundError:
        pass


# Save aura data to a file
def save_aura_data():
    data = {
        str(guild_id): {str(user_id): aura for user_id, aura in users.items()}
        for guild_id, users in user_aura.items()
    }
    with open('aura_data.json', 'w') as f:
        json.dump(data, f, indent=4)


# Load levels data from a file
def load_levels_data():
    try:
        with open('levels.json', 'r') as f:
            data = json.load(f)
            for guild_id, users in data.items():
                for user_id, level in users.items():
                    user_levels[int(guild_id)][int(user_id)] = level
    except FileNotFoundError:
        pass


# Save levels data to a file
def save_levels_data():
    data = {
        str(guild_id): {str(user_id): level for user_id, level in users.items()}
        for guild_id, users in user_levels.items()
    }
    with open('levels.json', 'w') as f:
        json.dump(data, f, indent=4)


# Leveling system: Update XP and check for level up
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    guild_id = message.guild.id
    user_id = message.author.id
    
    # Ensure user is initialized in the dictionaries
    if user_id not in user_experience[guild_id]:
        user_experience[guild_id][user_id] = 0
    if user_id not in user_aura[guild_id]:
        user_aura[guild_id][user_id] = 0
    if user_id not in user_levels[guild_id]:
        user_levels[guild_id][user_id] = 1

    user_experience[guild_id][user_id] += 10  # Increment XP by 10 for each message

    # Check for level up
    current_level = calculate_level(user_experience[guild_id][user_id])
    previous_level = user_levels[guild_id][user_id]
    if current_level > previous_level:
        user_levels[guild_id][user_id] = current_level
        save_levels_data()
        if current_level % 5 == 0 and not discord.utils.get(message.author.roles, name="Aura Wizard"):
            user_aura[guild_id][user_id] += 1000
            save_aura_data()
        await message.channel.send(f'Congratulations {message.author.mention}, you have reached level {current_level}!')

    await bot.process_commands(message)


# Function to calculate level based on XP
def calculate_level(xp):
    return xp // 100  # Assuming 100 XP per level


# Command to check your level
@bot.command(name='LVL')
async def check_level(ctx):
    guild_id = ctx.guild.id
    user_id = ctx.author.id
    level = user_levels[guild_id][user_id]
    await ctx.send(f'{ctx.author.display_name}, your current level is {level}.')


# Command to check the level of all users in the current guild
@bot.command(name='LVL-ALL')
async def check_all_levels(ctx):
    guild_id = ctx.guild.id
    level_info = []

    for member in ctx.guild.members:
        if member.id == bot.user.id:
            continue
        level = user_levels[guild_id][member.id]
        level_info.append(f'{member.display_name}: Level {level}')

    await ctx.send('\n'.join(level_info))


# Tell a joke
@bot.command(name='joke')
async def joke(ctx):
    await ctx.send(get_joke())


# Get a summarized article from Wikipedia
@bot.command(name='info')
async def info(ctx, *, subject):
    await ctx.send(get_wikipedia_summary(subject))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "rocket league" in (message.content).lower() or "rl" in (message.content).lower():
        await message.channel.send("Dude! Rocket League is a dead game.")
        await message.channel.send("Let's play Valorant instead.")

if __name__ == "__main__":
    bot.run(TOKEN)
