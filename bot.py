import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from collections import defaultdict


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Setting Permissions
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable the members intent

# Set a Prefix for Commands
bot = commands.Bot(command_prefix='/', intents=intents)

# Store members
members = []

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

# Check if the user invoking the command has "The Wizard" role
def is_wizard(ctx):
    return discord.utils.get(ctx.author.roles, name="Aura Wizard") is not None

# Bot Initialization
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    load_aura_data()

    # Get the server by name or ID
    guild = discord.utils.get(bot.guilds, name=GUILD) or discord.utils.get(bot.guilds, id=int(GUILD))

    print(f'Guild: {guild.name} (ID: {guild.id})')

    # Store existing members
    for member in guild.members:
        members.append(member)

# Welcome new members
@bot.event
async def on_member_join(member):
    members.append(member)
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to The Gang')

# Goodbye to leaving members
@bot.event
async def on_member_remove(member):
    members[:] = [m for m in members if m.id != member.id]  # Remove member by ID
    await member.create_dm()
    await member.dm_channel.send(f'Goodbye {member.name}. Never come back!')

# Leveling system: Update XP and check for level up
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = message.author.id
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

if __name__ == "__main__":
    bot.run(TOKEN)

