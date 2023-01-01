import aiohttp
import aiohttp
import asyncio
import discord
from discord.ext import commands
import os
import json
import difflib

class ModTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

        



async def setup(bot):
    await bot.add_cog(ModTools(bot))