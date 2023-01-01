import aiohttp
import aiohttp
import asyncio
import discord
from discord.ext import commands

USERAGENT = "Frostbyte/@WhenDawnEnds (contact on Twitter)"

class Animals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(brief="Sends a random cat image")
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search", headers={"User-Agent": USERAGENT}) as resp:
                data = await resp.json()
        em = discord.Embed(color=self.bot.main_color())
        em.set_image(url=data[0]["url"])
        await ctx.reply(embed=em)
    
    @commands.command(brief="Sends a random dog image")
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thedogapi.com/v1/images/search", headers={"User-Agent": USERAGENT}) as resp:
                data = await resp.json()
        em = discord.Embed(color=self.bot.main_color())
        em.set_image(url=data[0]["url"])
        await ctx.reply(embed=em)
        
    @commands.command(brief="Sends a random fox image")
    async def fox(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://randomfox.ca/floof/", headers={"User-Agent": USERAGENT}) as resp:
                data = await resp.json()
        em = discord.Embed(color=self.bot.main_color())
        em.set_image(url=data["image"])
        await ctx.reply(embed=em)
        
    @commands.command(brief="Sends a random red panda image")
    async def redpanda(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/img/red_panda", headers={"User-Agent": USERAGENT}) as resp:
                data = await resp.json()
        em = discord.Embed(color=self.bot.main_color())
        em.set_image(url=data["link"])
        await ctx.reply(embed=em)
        
    @commands.command(brief="Sends a random bird image")
    async def bird(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/img/birb", headers={"User-Agent": USERAGENT}) as resp:
                data = await resp.json()
        em = discord.Embed(color=self.bot.main_color())
        em.set_image(url=data["link"])
        await ctx.reply(embed=em)
        
    @commands.command(brief="Sends a random koala image")
    async def koala(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/img/koala", headers={"User-Agent": USERAGENT}) as resp:
                data = await resp.json()
        em = discord.Embed(color=self.bot.main_color())
        em.set_image(url=data["link"])
        await ctx.reply(embed=em)

    @commands.command(brief="Sends a random panda image")
    async def panda(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/img/panda", headers={"User-Agent": USERAGENT}) as resp:
                data = await resp.json()
        em = discord.Embed(color=self.bot.main_color())
        em.set_image(url=data["link"])
        await ctx.reply(embed=em)
        
    @commands.command(brief="Sends a random raccoon image")
    async def raccoon(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/img/raccoon", headers={"User-Agent": USERAGENT}) as resp:
                data = await resp.json()
        em = discord.Embed(color=self.bot.main_color())
        em.set_image(url=data["link"])
        await ctx.reply(embed=em)
        
    @commands.command(brief="Sends a random kangaroo image")
    async def kangaroo(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/img/kangaroo", headers={"User-Agent": USERAGENT}) as resp:
                data = await resp.json()
        em = discord.Embed(color=self.bot.main_color())
        em.set_image(url=data["link"])
        await ctx.reply(embed=em)

        
        
async def setup(bot):
    await bot.add_cog(Animals(bot))