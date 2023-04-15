# Bare minimal to test if Discord is responding
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os 
load_dotenv()


intents = discord.Intents.all()
intents.members = False
intents.messages = True
intents.presences = False
bot = discord.ext.commands.Bot(command_prefix="", status=discord.Status.idle, activity=discord.Activity(name="Skeleton Shell"),intents=intents)

@bot.event
async def on_ready():
    print("🕸️ Connected to Discord successfully!")
    print("🕸️ Logged in as: " + bot.user.name)
    print("🕸️ Bot ID: " + str(bot.user.id))
    print("🕸️ Discord.py version: " + discord.__version__)
    print("🕸️ You may now close this window.")
    

bot.run(os.getenv("TOKEN_PRODUCTION"))