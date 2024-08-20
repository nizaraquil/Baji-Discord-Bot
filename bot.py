import os
import re
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

# Dictionary to store user XP and Aura balances
user_experience = defaultdict(int)
user_aura = defaultdict(int)

# Load aura data from a file
def load_aura_data():
    try:
        with open('aura_data.json', 'r') as f:
            data = json.load(f)
            for user_id, aura in data.items():
                user_aura[int(user_id)] = aura
    except FileNotFoundError:
        pass

# Save aura data to a file
def save_aura_data():
    with open('aura_data.json', 'w') as f:
        json.dump(user_aura, f)

# Check if the user invoking the command has "Aura Wizard" role
def is_wizard(ctx):
    return discord.utils.get(ctx.author.roles, name="Aura Wizard") is not None

def get_joke():
    URL = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(URL).json()
    joke = f"{response['setup']} - {response['punchline']}"
    return joke

def get_wikipedia_summary(subject):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{subject}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        summary = data.get('extract', '')
        if len(summary) > 3990:
            summary = summary[:3990] + '...etc'
        return summary
    else:
        return "Error: Unable to fetch summary."

# Bot Initialization
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    load_aura_data()

    # Log details about all guilds the bot is part of
    for guild in bot.guilds:
        print(f'Connected to Guild: {guild.name} (ID: {guild.id})')

# Welcome new members
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to {member.guild.name}!')

# Goodbye to leaving members
@bot.event
async def on_member_remove(member):
    await member.create_dm()
    await member.dm_channel.send(f'Goodbye {member.name}. Never come back!')

# Leveling system: Update XP and check for level up
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = message.author.id
    
    # Add user to dictionaries if not already present
    if user_id not in user_experience:
        user_experience[user_id] = 0
    if user_id not in user_aura:
        user_aura[user_id] = 0

    user_experience[user_id] += 10  # Increment XP by 10 for each message

    # Check for level up
    current_level = calculate_level(user_experience[user_id])
    previous_level = calculate_level(user_experience[user_id] - 10)
    if current_level > previous_level:
        if current_level % 5 == 0 and not discord.utils.get(message.author.roles, name="Aura Wizard"):
            user_aura[user_id] += 1000
            save_aura_data()
        await message.channel.send(f'Congratulations {message.author.mention}, you have reached level {current_level}!')

    await bot.process_commands(message)

# Function to calculate level based on XP
def calculate_level(xp):
    return xp // 100  # Assuming 100 XP per level

# Command to add Aura to a user's wallet
@bot.command(name='AU+')
@commands.check(is_wizard)
async def add_aura(ctx, amount: int, member: discord.Member):
    user_aura[member.id] += amount
    save_aura_data()
    await ctx.send(f'{amount} Aura added to {member.display_name}')

# Command to subtract Aura from a user's wallet
@bot.command(name='AU-')
@commands.check(is_wizard)
async def subtract_aura(ctx, amount: int, member: discord.Member):
    user_aura[member.id] -= amount
    save_aura_data()
    await ctx.send(f'{amount} Aura subtracted from {member.display_name}')

# Command to check Aura balances
@bot.command(name='AURA')
async def check_aura(ctx):
    aura_info = []

    for member in ctx.guild.members:
        if member.id == bot.user.id:
            continue
        elif discord.utils.get(member.roles, name="Aura Wizard"):
            aura_balance = "\u221E"  # Infinity sign for Aura Wizard role
        else:
            aura_balance = user_aura[member.id]

        aura_info.append(f'{member.display_name}: {aura_balance} AU')

    await ctx.send('\n'.join(aura_info))

# Command to check your level
@bot.command(name='LVL')
async def check_level(ctx):
    user_id = ctx.author.id
    level = calculate_level(user_experience[user_id])
    await ctx.send(f'{ctx.author.display_name}, your current level is {level}.')

# Command to check the level of all users
@bot.command(name='LVL-ALL')
async def check_all_levels(ctx):
    level_info = []

    for member in ctx.guild.members:
        if member.id == bot.user.id:
            continue
        level = calculate_level(user_experience[member.id])
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


if __name__ == "__main__":
    bot.run(TOKEN)
