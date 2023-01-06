# Cog for handling stats channels and bot lists
# Shouldn't need any commands here

import aiohttp
import aiohttp
import asyncio
import discord
from discord.ext import commands
import os
import json
import difflib

def intToHumanReadable(num): # Whatever is done here, it is not me, it was copilot
    num = int(num)
    if num < 1000:
        return str(num)
    elif num < 1000000:
        return str(num / 1000) + "K"
    elif num < 1000000000:
        return str(num / 1000000) + "M"
    elif num < 1000000000000:
        return str(num / 1000000000) + "B"
    elif num < 1000000000000000:
        return str(num / 1000000000000) + "T"
    else:
        return str(num)


class StatsUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokens = {
            "dbl": os.getenv("DBL_TOKEN"), # top.gg
            "dblc": os.getenv("DBLC_TOKEN"), # discordbotlist.com
            "dbo": os.getenv("DBO_TOKEN"), # discord.boats
        }
        self.channels = {
            "servers": self.bot.get_channel(769594349138346044), # ╔ Serving {} servers
            "users": self.bot.get_channel(769594385578459178),   # ║ and {} users
            "release": self.bot.get_channel(801270816967753768), # ╚ on release {}
        }
        
    async def update_stats(self):
        # Update stats channels
        await self.channels["servers"].edit(name=f"╔ Serving {intToHumanReadable(len(self.bot.guilds))} servers")
        await self.channels["users"].edit(name=f"║ and {intToHumanReadable(len(self.bot.users))} users")
        await self.channels["release"].edit(name=f"╚ {self.bot.version}")
        # Open a session
        with aiohttp.ClientSession() as session:
            # Update top.gg
            if self.tokens["dbl"]:
                async with session.post(f"https://top.gg/api/bots/{self.bot.user.id}/stats", headers={"Authorization": self.tokens["dbl"]}, data={"server_count": len(self.bot.guilds)}) as r:
                    if r.status != 200:
                        await self.bot.bot_log.send(f"Error updating top.gg stats:\n {r.status} {r.reason}")
            # Update discordbotlist.com
            if self.tokens["dblc"]:
                async with session.post(f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats", headers={"Authorization": self.tokens["dblc"]}, data={"guilds": len(self.bot.guilds), "users": len(self.bot.users)}) as r:
                    if r.status != 200:
                        await self.bot.bot_log.send(f"Error updating discordbotlist.com stats:\n {r.status} {r.reason}")
            # Update discord.boats
            if self.tokens["dbo"]:
                async with session.post(f"https://discord.boats/api/bot/{self.bot.user.id}", headers={"Authorization": self.tokens["dbo"], "content-type": "application/json"}, data={"server_count": len(self.bot.guilds)}) as r:
                    if r.status != 200:
                        await self.bot.bot_log.send(f"Error updating discord.boats stats:\n {r.status} {r.reason}")

    async def on_ready(self):
        # Check if the bot is running production
        if self.bot.user.id == 732233716604076075: # THe most shittiest way to check if the bot is running production, but checking deployment didnt work
            await self.bot.wait_until_ready()
            while self.bot.is_ready():
                await self.update_stats()
                # Wait 30 minutes
                await asyncio.sleep(1800)


async def setup(bot):
    await bot.add_cog(StatsUpdater(bot))